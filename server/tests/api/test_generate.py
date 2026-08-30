from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.generate import get_ai_service
from app.ai.mock import MockAIService

app.dependency_overrides[get_ai_service] = lambda: MockAIService()

client = TestClient(app)

DATABASE_PATH = (
    Path(__file__).resolve().parents[3]
    / "database"
    / "samples"
    / "company.db"
)

def test_generate_sql():
    with DATABASE_PATH.open("rb") as file:
        session_response = client.post(
            "/database/session",
            data={
                "database_type": "sqlite",
            },
            files={
                "file": (
                    DATABASE_PATH.name,
                    file,
                    "application/octet-stream",
                )
            },
        )

    assert session_response.status_code == 200

    session_id = session_response.json()["session_id"]

    response = client.post(
        "/generate",
        json={
            "session_id": session_id,
            "question": (
                "Show the highest paid employees"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sql"]
    assert data["explanation"]
    assert 0 <= data["confidence"] <= 1


def test_generate_invalid_session():
    response = client.post(
        "/generate",
        json={
            "session_id": "does-not-exist",
            "question": "Show employees",
        },
    )

    assert response.status_code == 404