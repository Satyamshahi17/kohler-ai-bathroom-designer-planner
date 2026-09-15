"""Deterministic Cypher queries used by the product rules engine."""

GET_INCOMPATIBLE_PAIRS = """
MATCH (a:Product)-[:INCOMPATIBLE_WITH]->(b:Product)
RETURN a.id AS product_a, b.id AS product_b
ORDER BY product_a, product_b
"""

GET_COMPATIBLE_PRODUCTS = """
MATCH (p:Product)-[:COMPATIBLE_WITH]->(other:Product {id: $product_id})
RETURN p
ORDER BY p.category, p.name
"""

GET_THEME_FILTERED_PRODUCTS = """
MATCH (p:Product)-[:STYLED_AS]->(t:DesignTheme)
WHERE toLower(t.name) = toLower($theme)
RETURN p
ORDER BY p.category, p.name
"""

GET_REQUIRED_ACCESSORIES = """
MATCH (p:Product {id: $product_id})-[:REQUIRES_ACCESSORY]->(a:Accessory)
RETURN a
ORDER BY a.id
"""

GET_ACCESSORY_REQUIREMENTS = """
MATCH (a:Accessory {id: $accessory_id})-[r:REQUIRES]->(i:InfrastructureRequirement)
RETURN a.id AS accessory_id, i.name AS requirement, r.max_distance AS max_distance
"""

GET_LAYOUT_RULES = """
MATCH (p:Product {id: $product_id})-[:REQUIRES_INSTALLATION_ZONE]->(i:InfrastructureRequirement)
RETURN p.id AS product_id, i.name AS installation_zone
"""

GET_DIMENSION_LIMIT = """
MATCH (p:Product {id: $product_id})
RETURN p.width AS width, p.depth AS depth, p.height AS height
"""

GET_INFRASTRUCTURE_REQUIREMENTS = """
MATCH (p:Product {id: $product_id})-[r]->(i:InfrastructureRequirement)
WHERE type(r) IN [
    'REQUIRES_PLUMBING', 'REQUIRES_DRAIN', 'REQUIRES_WATER_SUPPLY',
    'REQUIRES_ELECTRICAL', 'REQUIRES_INSTALLATION_ZONE'
]
RETURN type(r) AS relationship, i.name AS requirement, r.max_distance AS max_distance
ORDER BY relationship, requirement
"""
