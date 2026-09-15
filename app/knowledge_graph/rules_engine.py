"""Deterministic product rules backed by Neo4j."""

from __future__ import annotations

from typing import Any

from . import queries
from .connection import Neo4jConnection


class KGRulesEngine:
    def __init__(self, connection: Neo4jConnection) -> None:
        self.connection = connection

    def get_incompatible_pairs(self) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_INCOMPATIBLE_PAIRS)

    def get_compatible_products(self, product_id: str) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_COMPATIBLE_PRODUCTS, product_id=product_id)

    def get_theme_filtered_products(self, theme: str) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_THEME_FILTERED_PRODUCTS, theme=theme)

    def get_required_accessories(self, product_id: str) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_REQUIRED_ACCESSORIES, product_id=product_id)

    def get_accessory_requirements(self, accessory_id: str) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_ACCESSORY_REQUIREMENTS, accessory_id=accessory_id)

    def get_layout_rules(self, product_id: str) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_LAYOUT_RULES, product_id=product_id)

    def get_dimension_limit(self, product_id: str) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_DIMENSION_LIMIT, product_id=product_id)

    def get_infrastructure_requirements(self, product_id: str) -> list[dict[str, Any]]:
        return self.connection.run(queries.GET_INFRASTRUCTURE_REQUIREMENTS, product_id=product_id)

    def is_compatible(self, product_a: str, product_b: str) -> bool:
        rows = self.connection.run(
            """
            MATCH (a:Product {id: $a})-[:INCOMPATIBLE_WITH]->(b:Product {id: $b})
            RETURN count(*) AS count
            """,
            a=product_a,
            b=product_b,
        )
        return not rows or rows[0]["count"] == 0
