import sqlite3

import pytest

import os
from sqlalchemy import create_engine, text

from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def sqlite_database(tmp_path):
    database_path = tmp_path / "test.db"

    connection = sqlite3.connect(database_path)
    
    connection.execute(
        """
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )
    
    connection.execute(
        """
        INSERT INTO departments (name)
        VALUES
            ('Engineering'),
            ('HR'),
            ('Finance')
        """
    )

    connection.execute(
        """
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            salary INTEGER NOT NULL,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
        """
    )

    connection.execute(
        """
        INSERT INTO employees (name, salary, department_id)
        VALUES
            ('Rahul', 1000000, 1),
            ('Amit', 1200000, 1),
            ('Priya', 1500000, 2)
        """
    )

    connection.commit()
    connection.close()

    return database_path

@pytest.fixture
def postgres_database():
    url = os.getenv("TEST_POSTGRES_URL")

    if not url:
        pytest.skip(
            "TEST_POSTGRES_URL is not set; skipping PostgreSQL tests"
        )

    engine_url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(engine_url)

    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS employees"))
        connection.execute(text("DROP TABLE IF EXISTS departments"))

        connection.execute(text(
            """
            CREATE TABLE departments (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        ))

        connection.execute(text(
            """
            INSERT INTO departments (name)
            VALUES ('Engineering'), ('HR'), ('Finance')
            """
        ))

        connection.execute(text(
            """
            CREATE TABLE employees (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                salary INTEGER NOT NULL,
                department_id INTEGER REFERENCES departments(id)
            )
            """
        ))

        connection.execute(text(
            """
            INSERT INTO employees (name, salary, department_id)
            VALUES
                ('Rahul', 1000000, 1),
                ('Amit', 1200000, 1),
                ('Priya', 1500000, 2)
            """
        ))

    engine.dispose()

    yield url

    cleanup_engine = create_engine(engine_url)
    with cleanup_engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS employees"))
        connection.execute(text("DROP TABLE IF EXISTS departments"))
    cleanup_engine.dispose()