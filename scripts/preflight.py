"""Local environment preflight for the Kohler AI Bathroom Designer."""
from __future__ import annotations

import importlib.util
import os
import sys

REQUIRED = {
    "flask": "Flask",
    "pydantic": "Pydantic",
    "dotenv": "python-dotenv",
    "pulp": "PuLP",
    "neo4j": "neo4j",
    "sentence_transformers": "sentence-transformers",
    "openai": "openai",
}


def main() -> int:
    missing = [label for module, label in REQUIRED.items() if importlib.util.find_spec(module) is None]
    print("Kohler AI Bathroom Designer — environment preflight")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Catalog mode: {os.getenv('PRODUCT_CATALOG_MODE', 'synthetic')}")
    if missing:
        print("Missing dependencies:")
        for item in missing:
            print(f"  - {item}")
        print("Install with: python -m pip install -r requirements.txt")
        return 1
    print("All Python dependencies are installed.")
    if not os.getenv("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY is not set; image extraction requires it.")
    if not os.getenv("NEO4J_PASSWORD"):
        print("Note: NEO4J_PASSWORD is not set; Neo4j-backed rules may be unavailable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
