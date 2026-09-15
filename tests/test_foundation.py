import pytest
pytest.importorskip("flask")

from app.main import create_app
from app.models.product import Product
from app.models.user_constraints import UserConstraints


def test_health_endpoint():
    client = create_app().test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_product_contract():
    product = Product(
        id="SYN-VAN-001",
        model_number="SYN-VAN-001",
        name="Zen Wall Vanity",
        category="vanity",
        price=1200,
        width=900,
        depth=500,
        height=600,
    )
    assert product.price == 1200


def test_user_constraints_contract():
    constraints = UserConstraints(
        budget=5000,
        theme="Japanese Zen",
        required_categories=["vanity", "faucet", "toilet", "shower"],
    )
    assert constraints.budget == 5000
