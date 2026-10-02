from app import create_app


def test_employee_can_get_tasks():
    app = create_app()
    client = app.test_client()

    response = client.get("/tasks?user_id=1")

    assert response.status_code == 200

    data = response.get_json()

    assert "tasks" in data
    assert len(data["tasks"]) >= 1

    for task in data["tasks"]:
        assert task["assigned_to"] == 1


def test_unauthorized_user_cannot_get_task():
    app = create_app()
    client = app.test_client()

    response = client.get("/tasks/6?user_id=99")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Task not found or access denied"

def test_employee_cannot_manage_task():
    app = create_app()
    client = app.test_client()

    response = client.put("/tasks/6/manage?user_id=1")

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == (
        "Task not found or user is not authorized to manage this task"
    )

def test_employee_cannot_approve_task():
    app = create_app()
    client = app.test_client()

    response = client.put("/tasks/6/approve?user_id=1")

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == (
        "Task not found or user is not authorized to approve this task"
    )
def test_manager_can_manage_pending_task():
    app = create_app()
    client = app.test_client()

    response = client.post(
    "/tasks",
    json={
        "title": "Automated test task",
        "description": "Task created for automated workflow testing.",
        "priority": "LOW",
        "created_by": 2,
        "assigned_to": 1
    }
)

    assert response.status_code == 201

    data = response.get_json()

    task_id = data["id"]

    response = client.put(
        f"/tasks/{task_id}/manage?user_id=2"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["task"]["id"] == task_id
    assert data["task"]["status"] == "MANAGED"
def test_complete_task_workflow():
    app = create_app()
    client = app.test_client()

    # Manager creates the task
    response = client.post(
        "/tasks",
        json={
            "title": "Complete workflow test",
            "description": "Testing the complete task lifecycle.",
            "priority": "MEDIUM",
            "created_by": 2,
            "assigned_to": 1
        }
    )

    assert response.status_code == 201

    task_id = response.get_json()["id"]

    # Manager manages the task
    response = client.put(
        f"/tasks/{task_id}/manage?user_id=2"
    )

    assert response.status_code == 200
    assert response.get_json()["task"]["status"] == "MANAGED"

    # Manager approves the task
    response = client.put(
        f"/tasks/{task_id}/approve?user_id=2"
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "APPROVED"

    # Employee starts the task
    response = client.put(
        f"/tasks/{task_id}/start?user_id=1"
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "IN_PROGRESS"

    # Employee completes the task
    response = client.put(
        f"/tasks/{task_id}/complete?user_id=1"
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "COMPLETED"