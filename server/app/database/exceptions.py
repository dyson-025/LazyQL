class DatabaseConnectionError(Exception):
    """Raised when LazyQL cannot connect to a database."""
    
class UnsafeQueryError(Exception):
    """Raised when a generated SQL query is not a safe, read-only SELECT."""