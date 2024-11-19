from fastapi.testclient import TestClient

from app.core.config import settings


def test_assign_order(
        client: TestClient
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/utils/health-check/",
    )
    assert response.status_code == 200
    content = response.text
    assert content == "true"
