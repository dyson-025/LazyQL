import pytest

from app.database.exceptions import DatabaseConnectionError
from app.database.postgres import PostgreSQLAdapter


def test_postgres_connection(postgres_database):
    db = PostgreSQLAdapter(postgres_database)

    assert db.connect() is True

    db.close()


def test_postgres_invalid_connection():
    db = PostgreSQLAdapter(
        "postgresql://baduser:badpass@localhost:5999/nonexistent?connect_timeout=3"
    )

    with pytest.raises(DatabaseConnectionError):
        db.connect()


def test_postgres_query_execution(postgres_database):
    db = PostgreSQLAdapter(postgres_database)

    db.connect()

    result = db.execute_query(
        "SELECT name, salary FROM employees ORDER BY salary DESC"
    )

    assert result["columns"] == ["name", "salary"]

    assert result["rows"] == [
        ["Priya", 1500000],
        ["Amit", 1200000],
        ["Rahul", 1000000],
    ]

    db.close()