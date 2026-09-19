"""Seed the Neo4j graph from the synthetic product catalog."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from app.products.catalog import load_products
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
    return list(
        dict.fromkeys(
            product.get("style_tags", [])
            + ([product["finish"]] if product.get("finish") else [])
        )
    )


def seed_database(
    connection: Neo4jConnection,
    catalog: list[Any],
) -> None:

    # Create constraints/indexes
    for constraint in CONSTRAINTS:
        connection.run(constraint)

    # Clear existing graph
    connection.run("MATCH (n) DETACH DELETE n")

    # catalog is list[Product]
    for product_model in catalog:

        # Convert Pydantic Product → dictionary
        product = product_model.model_dump()

        # Neo4j product properties
        connection.run(
            """
            MERGE (p:Product {id: $id})
            SET p.model_number = $model_number,
                p.name = $name,
                p.category = $category,
                p.price = $price,
                p.width = $width,
                p.depth = $depth,
                p.height = $height,
                p.description = $description,
                p.installation_type = $installation_type,
                p.faucet_configuration = $faucet_configuration,
                p.clearance_requirements = $clearance_requirements,
                p.infrastructure_requirements = $infrastructure_requirements

            MERGE (c:Category {name: $category})
            MERGE (p)-[:IN_CATEGORY]->(c)
            """,
            id=product["id"],
            model_number=product["model_number"],
            name=product["name"],
            category=product["category"],
            price=product["price"],
            width=product["width"],
            depth=product["depth"],
            height=product["height"],
            description=product["description"],
            installation_type=product.get("installation_type"),
            faucet_configuration=product.get("faucet_configuration"),
            clearance_requirements=str(
                product.get("clearance_requirements", {})
            ),
            infrastructure_requirements=product.get(
                "infrastructure_requirements", []
            ),
        )

        # -------------------------
        # Design themes
        # -------------------------

        for tag in _themes(product):
            if not tag:
                continue

            theme = THEME_NAMES.get(
                tag.lower().replace(" ", "_"),
                tag.title(),
            )

            connection.run(
                """
                MATCH (p:Product {id: $id})
                MERGE (t:DesignTheme {name: $theme})
                MERGE (p)-[:STYLED_AS]->(t)
                """,
                id=product["id"],
                theme=theme,
            )

        # -------------------------
        # Finish
        # -------------------------

        finish = product.get("finish")

        if finish:
            connection.run(
                """
                MATCH (p:Product {id: $id})
                MERGE (f:Finish {name: $finish})
                MERGE (p)-[:HAS_FINISH]->(f)
                """,
                id=product["id"],
                finish=finish,
            )

        # -------------------------
        # Required accessories
        # -------------------------

        for accessory_id in product.get(
            "required_accessories", []
        ):

            connection.run(
                """
                MATCH (p:Product {id: $product_id})
                MERGE (a:Accessory {id: $accessory_id})
                MERGE (p)-[:REQUIRES_ACCESSORY]->(a)
                """,
                product_id=product["id"],
                accessory_id=accessory_id,
            )

        # -------------------------
        # Infrastructure
        # -------------------------

        infrastructure = product.get(
            "infrastructure_requirements", []
        ) or []

        rel_map = {
            "plumbing": "REQUIRES_PLUMBING",
            "drain": "REQUIRES_DRAIN",
            "water_supply": "REQUIRES_WATER_SUPPLY",
            "electrical": "REQUIRES_ELECTRICAL",
            "installation_zone": "REQUIRES_INSTALLATION_ZONE",
        }

        for requirement in infrastructure:

            if isinstance(requirement, dict):
                key = requirement.get("type", "other")
                name = requirement.get("name")
                max_distance = requirement.get("max_distance")
            else:
                key = requirement
                name = requirement
                max_distance = None

            if not name:
                continue

            relationship = rel_map.get(
                key,
                "REQUIRES",
            )

            connection.run(
                f"""
                MATCH (p:Product {{id: $product_id}})
                MERGE (i:InfrastructureRequirement {{name: $name}})
                MERGE (p)-[r:{relationship}]->(i)
                SET r.max_distance = $max_distance
                """,
                product_id=product["id"],
                name=name,
                max_distance=max_distance,
            )

        # -------------------------
        # Compatibility
        # -------------------------

        compatibility = product.get(
            "compatibility", []
        ) or []

        for compatible_id in compatibility:

            connection.run(
                """
                MATCH (p:Product {id: $product_id})
                MATCH (q:Product {id: $other_id})
                MERGE (p)-[:COMPATIBLE_WITH]->(q)
                """,
                product_id=product["id"],
                other_id=compatible_id,
            )


if __name__ == "__main__":

    load_dotenv()

    connection = Neo4jConnection(
        uri=os.environ["NEO4J_URI"],
        username=os.environ["NEO4J_USERNAME"],
        password=os.environ["NEO4J_PASSWORD"],
        database=os.environ["NEO4J_DATABASE"],
    )

    catalog = load_products()

    try:
        connection.connect()

        seed_database(
            connection,
            catalog,
        )

        print(
            f"✅ Successfully seeded {len(catalog)} products into Neo4j."
        )

    finally:
        connection.close()