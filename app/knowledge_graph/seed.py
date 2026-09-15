"""Seed the Neo4j graph from the synthetic product catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.products.catalog import ProductCatalog
from .connection import Neo4jConnection
from .schema import CONSTRAINTS


THEME_NAMES = {
    "japanese_zen": "Japanese Zen",
    "modern": "Modern",
    "minimalist": "Minimalist",
    "traditional": "Traditional",
    "spa": "Spa",
    "warm": "Warm",
    "industrial": "Industrial",
}


def _themes(product: dict[str, Any]) -> list[str]:
    return list(dict.fromkeys(product.get("style_tags", []) + [product.get("finish", "")]))


def seed_database(connection: Neo4jConnection, catalog: ProductCatalog) -> None:
    for constraint in CONSTRAINTS:
        connection.run(constraint)

    connection.run("MATCH (n) DETACH DELETE n")

    products = catalog.products
    for product in products:
        connection.run(
            """
            MERGE (p:Product {id: $id})
            SET p.model_number=$model_number, p.name=$name, p.category=$category,
                p.price=$price, p.width=$width, p.depth=$depth, p.height=$height,
                p.description=$description, p.installation_type=$installation_type,
                p.faucet_configuration=$faucet_configuration,
                p.clearance_requirements=$clearance_requirements,
                p.infrastructure_requirements=$infrastructure_requirements
            MERGE (c:Category {name: $category})
            MERGE (p)-[:IN_CATEGORY]->(c)
            """,
            **product,
            faucet_configuration=product.get("faucet_configuration"),
        )

        for tag in _themes(product):
            if not tag:
                continue
            theme = THEME_NAMES.get(tag.lower().replace(" ", "_"), tag.title())
            connection.run(
                """
                MATCH (p:Product {id: $id})
                MERGE (t:DesignTheme {name: $theme})
                MERGE (p)-[:STYLED_AS]->(t)
                """,
                id=product["id"], theme=theme,
            )

        finish = product.get("finish")
        if finish:
            connection.run(
                """
                MATCH (p:Product {id: $id})
                MERGE (f:Finish {name: $finish})
                MERGE (p)-[:HAS_FINISH]->(f)
                """,
                id=product["id"], finish=finish,
            )

        for accessory_id in product.get("required_accessories", []):
            connection.run(
                """
                MATCH (p:Product {id: $product_id})
                MERGE (a:Accessory {id: $accessory_id})
                MERGE (p)-[:REQUIRES_ACCESSORY]->(a)
                """,
                product_id=product["id"], accessory_id=accessory_id,
            )

        infra = product.get("infrastructure_requirements", []) or []
        # The synthetic catalog currently stores infrastructure requirements as
        # a flat list. Keep support for richer dict-shaped data as well.
        if isinstance(infra, dict):
            items = []
            for key, value in infra.items():
                values = value if isinstance(value, list) else [value]
                items.extend((key, item) for item in values)
        else:
            items = [(item, item) for item in infra]

        rel_map = {
            "plumbing": "REQUIRES_PLUMBING",
            "drain": "REQUIRES_DRAIN",
            "water_supply": "REQUIRES_WATER_SUPPLY",
            "electrical": "REQUIRES_ELECTRICAL",
            "installation_zone": "REQUIRES_INSTALLATION_ZONE",
        }
        for key, requirement in items:
            rel = rel_map.get(key, "REQUIRES")
            name = requirement if isinstance(requirement, str) else requirement.get("name")
            max_distance = requirement.get("max_distance") if isinstance(requirement, dict) else None
            if not name:
                continue
            connection.run(
                f"""
                MATCH (p:Product {{id: $product_id}})
                MERGE (i:InfrastructureRequirement {{name: $name}})
                MERGE (p)-[r:{rel}]->(i)
                SET r.max_distance = $max_distance
                """,
                product_id=product["id"], name=name, max_distance=max_distance,
            )

        compatibility = product.get("compatibility", [])
        compatible_ids = compatibility if isinstance(compatibility, list) else compatibility.get("compatible_with", [])
        incompatible_ids = [] if isinstance(compatibility, list) else compatibility.get("incompatible_with", [])
        for compatible_id in compatible_ids:
            connection.run(
                """
                MATCH (p:Product {id: $product_id})
                MERGE (q:Product {id: $other_id})
                MERGE (p)-[:COMPATIBLE_WITH]->(q)
                """,
                product_id=product["id"], other_id=compatible_id,
            )

        for incompatible_id in incompatible_ids:
            connection.run(
                """
                MATCH (p:Product {id: $product_id})
                MERGE (q:Product {id: $other_id})
                MERGE (p)-[:INCOMPATIBLE_WITH]->(q)
                """,
                product_id=product["id"], other_id=incompatible_id,
            )
