"""Neo4j connection abstraction with graceful unavailable-database handling."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    GraphDatabase = None


class Neo4jConnection:
    def __init__(self, uri: str, username: str, password: str, database: str = "067d9bee") -> None:
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver = None

    def connect(self) -> None:
        if GraphDatabase is None:
            raise RuntimeError("Neo4j driver is not installed. Install the project dependencies first.")
        self._driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        self._driver.verify_connectivity()

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    @property
    def available(self) -> bool:
        return self._driver is not None

    @contextmanager
    def session(self) -> Iterator[Any]:
        if self._driver is None:
            raise RuntimeError("Neo4j connection is not initialized. Call connect() first.")
        with self._driver.session(database=self.database) as session:
            yield session

    def run(self, query: str, **parameters: Any) -> list[dict[str, Any]]:
        with self.session() as session:
            return [record.data() for record in session.run(query, **parameters)]
