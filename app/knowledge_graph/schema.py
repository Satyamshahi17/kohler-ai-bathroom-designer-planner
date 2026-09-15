"""Neo4j schema definitions for the synthetic Kohler bathroom catalog."""

CONSTRAINTS = [
    "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT finish_name IF NOT EXISTS FOR (f:Finish) REQUIRE f.name IS UNIQUE",
    "CREATE CONSTRAINT theme_name IF NOT EXISTS FOR (t:DesignTheme) REQUIRE t.name IS UNIQUE",
    "CREATE CONSTRAINT accessory_id IF NOT EXISTS FOR (a:Accessory) REQUIRE a.id IS UNIQUE",
    "CREATE CONSTRAINT infrastructure_name IF NOT EXISTS FOR (i:InfrastructureRequirement) REQUIRE i.name IS UNIQUE",
]

RELATIONSHIPS = [
    "STYLED_AS",
    "HAS_FINISH",
    "COMPATIBLE_WITH",
    "INCOMPATIBLE_WITH",
    "REQUIRES",
    "REQUIRES_ACCESSORY",
    "REQUIRES_PLUMBING",
    "REQUIRES_DRAIN",
    "REQUIRES_WATER_SUPPLY",
    "REQUIRES_ELECTRICAL",
    "REQUIRES_INSTALLATION_ZONE",
]
