from app.database.safety import validate_readonly_sql
from app.database.exceptions import UnsafeQueryError
import shutil
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.database.connection import create_database_adapter
from app.database.exceptions import DatabaseConnectionError
from app.database.session_manager import session_manager
from app.models.database import DatabaseConfig
from app.models.schema import DatabaseSchema
from app.models.session import (
    DatabaseSession,
    QueryRequest,
    QueryResponse,
)


router = APIRouter(
    prefix="/database",
    tags=["database"],
)


@router.post(
    "/schema",
    response_model=DatabaseSchema,
)
def get_schema(session_id: str):
    try:
        db = session_manager.get_session(
            session_id
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Database session not found",
        ) from exc

    return db.get_schema()


@router.post(
    "/execute",
    response_model=QueryResponse,
)
def execute_query(request: QueryRequest):
    try:
        db = session_manager.get_session(
            request.session_id
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Database session not found",
        ) from exc

    try:
        validate_readonly_sql(request.sql)
    except UnsafeQueryError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    result = db.execute_query(request.sql)

    return QueryResponse(
        success=True,
        columns=result["columns"],
        rows=result["rows"],
    )


@router.post(
    "/session",
    response_model=DatabaseSession,
)
def create_database_session(
    database_type: str = Form(...),
    connection_url: str | None = Form(None),
    file: UploadFile | None = File(None),
):
    if database_type == "sqlite":
        if file is None:
            raise HTTPException(
                status_code=400,
                detail="SQLite database file is required",
            )

        suffix = Path(
            file.filename or ""
        ).suffix.lower()

        if suffix not in {
            ".db",
            ".sqlite",
            ".sqlite3",
        }:
            raise HTTPException(
                status_code=400,
                detail="Unsupported SQLite file type",
            )

        temp_dir = Path(
            tempfile.mkdtemp()
        )

        temp_path = temp_dir / (
            file.filename or "database.db"
        )

        try:
            with temp_path.open("wb") as destination:
                shutil.copyfileobj(
                    file.file,
                    destination,
                )

            # SQLiteAdapter expects a filesystem path,
            # not a sqlite:/// connection URL.
            connection_url = temp_path.as_posix()

        except Exception:
            temp_path.unlink(
                missing_ok=True
            )
            raise

    elif database_type == "postgresql":
        if not connection_url:
            raise HTTPException(
                status_code=400,
                detail=(
                    "PostgreSQL connection URL "
                    "is required"
                ),
            )

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported database type",
        )

    config = DatabaseConfig(
        database_type=database_type,
        connection_url=connection_url,
    )

    db = create_database_adapter(config)

    try:
        db.connect()

    except DatabaseConnectionError as exc:
        db.close()

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    session_id = session_manager.create_session(
        db
    )

    return DatabaseSession(
        session_id=session_id,
        database_type=database_type,
    )