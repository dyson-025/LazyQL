import pytest
from app.database.safety import validate_readonly_sql
from app.database.exceptions import UnsafeQueryError


def test_allows_select():
    validate_readonly_sql("SELECT * FROM employees;")


def test_blocks_delete():
    with pytest.raises(UnsafeQueryError):
        validate_readonly_sql("DELETE FROM employees;")


def test_blocks_drop():
    with pytest.raises(UnsafeQueryError):
        validate_readonly_sql("DROP TABLE employees;")


def test_blocks_stacked_statements():
    with pytest.raises(UnsafeQueryError):
        validate_readonly_sql("SELECT * FROM employees; DROP TABLE employees;")