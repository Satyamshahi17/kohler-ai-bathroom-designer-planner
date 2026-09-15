from app.knowledge_graph.schema import CONSTRAINTS, RELATIONSHIPS
from app.knowledge_graph.rules_engine import KGRulesEngine


class FakeConnection:
    def __init__(self):
        self.calls = []

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        if "INCOMPATIBLE_WITH" in query:
            return [{"product_a": "a", "product_b": "b"}]
        return []


def test_schema_defines_required_graph_entities():
    assert any("Product" in c for c in CONSTRAINTS)
    assert "COMPATIBLE_WITH" in RELATIONSHIPS
    assert "INCOMPATIBLE_WITH" in RELATIONSHIPS
    assert "REQUIRES_ACCESSORY" in RELATIONSHIPS
    assert "REQUIRES_ELECTRICAL" in RELATIONSHIPS


def test_rules_engine_delegates_deterministic_incompatibility_query():
    conn = FakeConnection()
    engine = KGRulesEngine(conn)
    assert engine.get_incompatible_pairs() == [{"product_a": "a", "product_b": "b"}]
    assert len(conn.calls) == 1


def test_is_compatible_rejects_explicit_incompatibility():
    class PairConnection(FakeConnection):
        def run(self, query, **parameters):
            if "count(*)" in query:
                return [{"count": 1}]
            return super().run(query, **parameters)

    assert KGRulesEngine(PairConnection()).is_compatible("a", "b") is False


def test_rules_engine_can_query_theme_and_accessories():
    conn = FakeConnection()
    engine = KGRulesEngine(conn)
    engine.get_theme_filtered_products("Japanese Zen")
    engine.get_required_accessories("SYN-VAN-001")
    engine.get_infrastructure_requirements("SYN-VAN-001")
    assert len(conn.calls) == 3
