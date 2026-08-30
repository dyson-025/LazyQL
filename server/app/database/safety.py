import sqlglot
from sqlglot.expressions import Select

from .exceptions import UnsafeQueryError


def validate_readonly_sql(sql: str) -> None:
    """
    Ensures the given SQL is a single, read-only SELECT statement.
    Raises UnsafeQueryError if it isn't.
    """
    try:
        statements = sqlglot.parse(sql)
    except Exception as exc:
        raise UnsafeQueryError("Unable to parse SQL query") from exc

    if statements is None or len(statements) == 0:
        raise UnsafeQueryError("Empty SQL query")

    if len(statements) > 1:
        raise UnsafeQueryError(
            "Multiple SQL statements are not allowed"
        )

    statement = statements[0]

    if not isinstance(statement, Select):
        raise UnsafeQueryError(
            "Only SELECT statements are allowed"
        )