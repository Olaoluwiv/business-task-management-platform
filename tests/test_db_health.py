from app import create_app


def test_db_health():
    app = create_app()
    client = app.test_client()

    response = client.get("/db-health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["database"] == "task_management"
