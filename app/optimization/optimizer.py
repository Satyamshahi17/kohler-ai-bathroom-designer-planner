"""PuLP integer optimizer for product bundles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from app.models.product import Product
from app.recommendation.hybrid_ranker import RankedProduct
from .accessories import accessory_catalog, required_accessories
from .constraints import has_incompatibility

try:
    import pulp
except ImportError:  # pragma: no cover - exercised in dependency-missing environments
    pulp = None


@dataclass(frozen=True)
class Bundle:
    products: tuple[Product, ...]
    accessories: tuple[Product, ...]
    total_product_cost: float
    total_accessory_cost: float
    total_cost: float
    score: float
    budget_feasible: bool
    constraint_satisfaction: dict[str, bool] = field(default_factory=dict)
    budget_shortfall: float = 0.0

    @property
    def product_ids(self) -> tuple[str, ...]:
        return tuple(p.id for p in self.products)

    def as_dict(self) -> dict:
        return {
            "products": [p.model_dump() for p in self.products],
            "accessories": [p.model_dump() for p in self.accessories],
            "product_ids": list(self.product_ids),
            "total_product_cost": self.total_product_cost,
            "total_accessory_cost": self.total_accessory_cost,
            "total_cost": self.total_cost,
            "score": self.score,
            "budget_feasible": self.budget_feasible,
            "budget_shortfall": self.budget_shortfall,
            "constraint_satisfaction": self.constraint_satisfaction,
        }


class BundleOptimizer:
    """Select exactly one product per required category and required accessories.

    PuLP is the authority for the discrete optimization. Explicit incompatibility
    pairs are hard constraints; accessory costs are included in the budget.
    """

    def __init__(self, catalog: list[Product]):
        self.catalog = catalog
        self.products_by_id = {p.id: p for p in catalog}
        self.accessories = accessory_catalog(catalog)

    def optimize(
        self,
        ranked: dict[str, list[RankedProduct]],
        budget: float,
        *,
        top_k: int = 3,
        incompatible_pairs: Iterable[tuple[str, str]] = (),
    ) -> list[Bundle]:
        if pulp is None:
            raise RuntimeError("PuLP is required for bundle optimization. Install dependencies from requirements.txt.")
        categories = list(ranked)
        if not categories:
            raise ValueError("At least one required category is needed.")
        candidates = {c: [r.product for r in ranked[c]] for c in categories}
        if any(not values for values in candidates.values()):
            raise ValueError("No candidates available for one or more required categories.")
        score_lookup = {r.product.id: float(r.hybrid_score) for values in ranked.values() for r in values}
        incompat = [tuple(pair) for pair in incompatible_pairs]

        solutions = self._solve_many(candidates, score_lookup, budget, top_k, incompat, enforce_budget=True)
        if solutions:
            return solutions

        # Spec-required fallback: find the best bundle without the budget constraint
        # and report the actual shortfall rather than pretending it fits.
        fallback = self._solve_many(candidates, score_lookup, budget, 1, incompat, enforce_budget=False)
        return fallback

    def _solve_many(self, candidates, score_lookup, budget, top_k, incompat, *, enforce_budget):
        selected_solutions: list[Bundle] = []
        no_goods: list[set[str]] = []
        for _ in range(top_k):
            bundle = self._solve_once(candidates, score_lookup, budget, incompat, enforce_budget, no_goods)
            if bundle is None:
                break
            selected_solutions.append(bundle)
            no_goods.append(set(bundle.product_ids))
        return selected_solutions

    def _solve_once(self, candidates, score_lookup, budget, incompat, enforce_budget, no_goods):
        problem = pulp.LpProblem("kohler_bathroom_bundle", pulp.LpMaximize)
        x = {p.id: pulp.LpVariable(f"x_{p.id}", cat=pulp.LpBinary)
             for values in candidates.values() for p in values}
        accessory_ids = sorted({aid for values in candidates.values() for p in values for aid in p.required_accessories})
        y = {aid: pulp.LpVariable(f"y_{aid}", cat=pulp.LpBinary) for aid in accessory_ids}

        # Exactly one product for every requested category.
        for category, values in candidates.items():
            problem += pulp.lpSum(x[p.id] for p in values) == 1, f"exactly_one_{category}"

        # Required accessories are activated whenever their parent product is selected.
        for values in candidates.values():
            for p in values:
                for aid in p.required_accessories:
                    if aid not in y:
                        raise ValueError(f"Required accessory {aid} not found in catalog")
                    problem += x[p.id] <= y[aid], f"accessory_{p.id}_{aid}"

        # Explicit incompatibility is symmetric regardless of input ordering.
        for a, b in incompat:
            if a in x and b in x:
                problem += x[a] + x[b] <= 1, f"incompatible_{a}_{b}"

        # Exclude previously returned product combinations for Top-N solutions.
        for i, ids in enumerate(no_goods):
            vars_in_solution = [x[pid] for pid in ids if pid in x]
            if vars_in_solution:
                problem += pulp.lpSum(vars_in_solution) <= len(vars_in_solution) - 1, f"no_good_{i}"

        product_cost = pulp.lpSum(p.price * x[p.id] for values in candidates.values() for p in values)
        accessory_cost = pulp.lpSum(self.accessories[aid].price * y[aid] for aid in accessory_ids)
        total_cost = product_cost + accessory_cost
        if enforce_budget:
            problem += total_cost <= budget, "budget"

        # Fit score is primary; a tiny cost preference makes ties deterministic.
        objective = pulp.lpSum(score_lookup.get(p.id, 0.0) * x[p.id] for values in candidates.values() for p in values)
        objective -= pulp.lpSum((p.price / max(budget, 1.0)) * 1e-5 * x[p.id] for values in candidates.values() for p in values)
        problem += objective
        status = problem.solve(pulp.PULP_CBC_CMD(msg=False))
        if pulp.LpStatus[status] != "Optimal":
            return None

        selected = [p for values in candidates.values() for p in values if pulp.value(x[p.id]) > 0.5]
        accessories = required_accessories(selected, self.accessories)
        product_total = round(sum(p.price for p in selected), 2)
        accessory_total = round(sum(a.price for a in accessories), 2)
        total = round(product_total + accessory_total, 2)
        score = round(sum(score_lookup.get(p.id, 0.0) for p in selected), 6)
        feasible = total <= budget + 1e-9
        return Bundle(
            products=tuple(selected), accessories=tuple(accessories),
            total_product_cost=product_total, total_accessory_cost=accessory_total,
            total_cost=total, score=score, budget_feasible=feasible,
            budget_shortfall=round(max(0.0, total - budget), 2),
            constraint_satisfaction={"one_per_category": True, "incompatibilities": True,
                                     "required_accessories": True, "budget": feasible},
        )
