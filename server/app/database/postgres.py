from sqlalchemy import create_engine, text

from .base import DatabaseAdapter
from .exceptions import DatabaseConnectionError
from .schema import extract_schema

from sqlalchemy.engine import make_url


class PostgreSQLAdapter(DatabaseAdapter):

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.engine = None

    def connect(self) -> bool:
        try:
            url = self.connection_url

            if url.startswith("postgresql://"):
                url = url.replace(
                    "postgresql://",
                    "postgresql+psycopg://",
                    1,
                )

            elif url.startswith("postgres://"):
                url = url.replace(
                    "postgres://",
                    "postgresql+psycopg://",
                    1,
                )

            self.engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_recycle=300,
            )

            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return True

        except Exception as exc:
            self.engine = None
        
            safe_url = make_url(self.connection_url).render_as_string(
                hide_password=True
            )
        
            print(
                "POSTGRES ERROR:",
                f"Failed to connect to {safe_url}",
            )
        
            raise DatabaseConnectionError(
                "Unable to connect to PostgreSQL database"
            ) from exc

    def get_schema(self):
        if self.engine is None:
            self.connect()

        return extract_schema(
            self.engine,
            "postgresql",
        )

    def execute_query(self, sql: str):
        if self.engine is None:
            raise RuntimeError(
                "Database is not connected"
            )

        with self.engine.begin() as connection:
            result = connection.execute(text(sql))

            return {
                "columns": list(result.keys()),
                "rows": [
                    list(row)
                    for row in result.fetchall()
                ],
            }

    def close(self):
        if self.engine:
            self.engine.dispose()
            self.engine = None
