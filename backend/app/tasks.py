from flask import Blueprint, request, g
from app.db import get_db_connection


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.post("/tasks")
def create_task():
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority")
    created_by = g.user_id
    assigned_to = data.get("assigned_to")

    if not title or not description or not priority:
        return {
            "error": "title, description, and priority are required"
        }, 400
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to
                )
                VALUES (%s, %s, %s, 'PENDING', %s, %s)
                RETURNING id, title, description, priority, status,
                          created_by, assigned_to, due_date,
                          created_at, updated_at;
                """,
                (
                    title,
                    description,
                    priority,
                    created_by,
                    assigned_to,
                ),
            )

            task = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    new_status,
                    details
                )
                VALUES (%s, %s, 'TASK_CREATED', 'PENDING', %s);
                """,
                (
                    task[0],
                    created_by,
                    "Task created",
                ),
            )

        connection.commit()

        return {
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "priority": task[3],
            "status": task[4],
            "created_by": task[5],
            "assigned_to": task[6],
            "due_date": task[7],
            "created_at": task[8].isoformat(),
            "updated_at": task[9].isoformat(),
        }, 201

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to create task",
            "details": str(error)
        }, 500

    finally:
        connection.close()

@tasks_bp.get("/tasks")
def get_tasks():
    user_id = g.user_id

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at
                FROM tasks
                WHERE assigned_to = %s
                   OR created_by = %s
                ORDER BY created_at DESC;
                """,
                (user_id, user_id),
            )

            rows = cursor.fetchall()

        tasks = []

        for row in rows:
            tasks.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "priority": row[3],
                "status": row[4],
                "created_by": row[5],
                "assigned_to": row[6],
                "due_date": row[7].isoformat() if row[7] else None,
                "created_at": row[8].isoformat(),
                "updated_at": row[9].isoformat(),
            })

        return {
            "tasks": tasks
        }, 200

    except Exception as error:
        return {
            "error": "Failed to retrieve tasks",
            "details": str(error)
        }, 500

    finally:
        connection.close()

@tasks_bp.get("/tasks/<int:task_id>")
def get_task(task_id):
    user_id = g.user_id

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at
                FROM tasks
                WHERE id = %s
                  AND (assigned_to = %s OR created_by = %s);
                """,
                (task_id, user_id, user_id),
            )

            task = cursor.fetchone()

        if not task:
            return {
                "error": "Task not found or access denied"
            }, 404

        return {
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "priority": task[3],
            "status": task[4],
            "created_by": task[5],
            "assigned_to": task[6],
            "due_date": task[7].isoformat() if task[7] else None,
            "created_at": task[8].isoformat(),
            "updated_at": task[9].isoformat(),
        }, 200

    except Exception as error:
        return {
            "error": "Failed to retrieve task",
            "details": str(error)
        }, 500

    finally:
        connection.close()

@tasks_bp.put("/tasks/<int:task_id>")
def update_task(task_id):
    user_id = g.user_id
    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "Request body is required"
        }, 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Check that the task exists and the user has access.
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date
                FROM tasks
                WHERE id = %s
                  AND (assigned_to = %s OR created_by = %s);
                """,
                (task_id, user_id, user_id),
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or access denied"
                }, 404

            # Keep existing values when a field is not supplied.
            title = data.get("title", task[1])
            description = data.get("description", task[2])
            priority = data.get("priority", task[3])
            due_date = data.get("due_date", task[7])

            if not title or not description or not priority:
                return {
                    "error": "title, description, and priority cannot be empty"
                }, 400

            cursor.execute(
                """
                UPDATE tasks
                SET
                    title = %s,
                    description = %s,
                    priority = %s,
                    due_date = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at;
                """,
                (
                    title,
                    description,
                    priority,
                    due_date,
                    task_id,
                ),
            )

            updated_task = cursor.fetchone()

            # Record the update in the audit history.
            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    old_status,
                    new_status,
                    details
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    task_id,
                    user_id,
                    "TASK_UPDATED",
                    task[4],
                    updated_task[4],
                    "Task information updated",
                ),
            )

        connection.commit()

        return {
            "id": updated_task[0],
            "title": updated_task[1],
            "description": updated_task[2],
            "priority": updated_task[3],
            "status": updated_task[4],
            "created_by": updated_task[5],
            "assigned_to": updated_task[6],
            "due_date": updated_task[7].isoformat()
                if updated_task[7] else None,
            "created_at": updated_task[8].isoformat(),
            "updated_at": updated_task[9].isoformat(),
        }, 200

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to update task",
            "details": str(error)
        }, 500

    finally:
        connection.close()
@tasks_bp.put("/tasks/<int:task_id>/approve")
def approve_task(task_id):
    user_id = g.user_id
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Verify that the user is the manager/creator of the task.
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at
                FROM tasks
                WHERE id = %s
                  AND created_by = %s;
                """,
                (task_id, user_id),
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to approve this task"
                }, 403

            # A task can only be approved when it is MANAGED.
            if task[4] != "PENDING_APPROVAL":
                return {
                    "error": f"Task cannot be approved from status {task[4]}"
                }, 400

            cursor.execute(
                """
                UPDATE tasks
                SET
                    status = 'APPROVED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at;
                """,
                (task_id,),
            )

            approved_task = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    old_status,
                    new_status,
                    details
                )
                VALUES (%s, %s, 'TASK_APPROVED', %s, %s, %s);
                """,
                (
                    task_id,
                    user_id,
                    task[4],
                    approved_task[4],
                    "Task approved by manager",
                ),
            )
            cursor.execute(
                """
                INSERT INTO approvals (
                    task_id,
                    reviewed_by,
                    decision,
                    comment
                )
                VALUES (%s, %s, %s, %s);
                """,
                (
                    task_id,
                    user_id,
                    "APPROVED",
                    "Task approved by manager",
                ),
            )

        connection.commit()

        return {
            "id": approved_task[0],
            "title": approved_task[1],
            "description": approved_task[2],
            "priority": approved_task[3],
            "status": approved_task[4],
            "created_by": approved_task[5],
            "assigned_to": approved_task[6],
            "due_date": approved_task[7].isoformat()
                if approved_task[7] else None,
            "created_at": approved_task[8].isoformat(),
            "updated_at": approved_task[9].isoformat(),
        }, 200

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to approve task",
            "details": str(error)
        }, 500

    finally:
        connection.close()
@tasks_bp.put("/tasks/<int:task_id>/start")
def start_task(task_id):
    user_id = g.user_id
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Verify that the user is the employee assigned to the task.
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at
                FROM tasks
                WHERE id = %s
                  AND assigned_to = %s;
                """,
                (task_id, user_id),
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to start this task"
                }, 404

            # A task can only be started when it is APPROVED.
            if task[4] != "MANAGED":
                return {
                    "error": f"Task cannot be started from status {task[4]}"
                }, 400

            cursor.execute(
                """
                UPDATE tasks
                SET
                    status = 'IN_PROGRESS',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at;
                """,
                (task_id,),
            )

            started_task = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    old_status,
                    new_status,
                    details
                )
                VALUES (%s, %s, 'TASK_STARTED', %s, %s, %s);
                """,
                (
                    task_id,
                    user_id,
                    task[4],
                    started_task[4],
                    "Task started by assigned employee",
                ),
            )

        connection.commit()

        return {
            "id": started_task[0],
            "title": started_task[1],
            "description": started_task[2],
            "priority": started_task[3],
            "status": started_task[4],
            "created_by": started_task[5],
            "assigned_to": started_task[6],
            "due_date": started_task[7].isoformat()
                if started_task[7] else None,
            "created_at": started_task[8].isoformat(),
            "updated_at": started_task[9].isoformat(),
        }, 200

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to start task",
            "details": str(error)
        }, 500

    finally:
        connection.close()
@tasks_bp.put("/tasks/<int:task_id>/complete")
def complete_task(task_id):
    user_id = g.user_id
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Verify that the user is the employee assigned to the task.
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at
                FROM tasks
                WHERE id = %s
                  AND assigned_to = %s;
                """,
                (task_id, user_id),
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to complete this task"
                }, 404

            # A task can only be completed when it is IN_PROGRESS.
            if task[4] != "IN_PROGRESS":
                return {
                    "error": f"Task cannot be completed from status {task[4]}"
                }, 400

            cursor.execute(
                """
                UPDATE tasks
                SET
                    status = 'PENDING_APPROVAL',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING
                    id,
                    title,
                    description,
                    priority,
                    status,
                    created_by,
                    assigned_to,
                    due_date,
                    created_at,
                    updated_at;
                """,
                (task_id,),
            )

            completed_task = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    old_status,
                    new_status,
                    details
                )
                VALUES (%s, %s, 'TASK_COMPLETED', %s, %s, %s);
                """,
                (
                    task_id,
                    user_id,
                    task[4],
                    completed_task[4],
                    "Task completed by assigned employee",
                ),
            )

        connection.commit()

        return {
            "id": completed_task[0],
            "title": completed_task[1],
            "description": completed_task[2],
            "priority": completed_task[3],
            "status": completed_task[4],
            "created_by": completed_task[5],
            "assigned_to": completed_task[6],
            "due_date": completed_task[7].isoformat()
                if completed_task[7] else None,
            "created_at": completed_task[8].isoformat(),
            "updated_at": completed_task[9].isoformat(),
        }, 200

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to complete task",
            "details": str(error)
        }, 500

    finally:
        connection.close()
@tasks_bp.put("/tasks/<int:task_id>/reject")
def reject_task(task_id):
    user_id = g.user_id

    data = request.get_json(silent=True) or {}

    rejection_comment = data.get("comment", "").strip()

    if not rejection_comment:
        return {"error": "rejection comment is required"}, 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, status
                FROM tasks
                WHERE id = %s
                  AND created_by = %s
                """,
                (task_id, user_id)
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to reject this task"
                }, 403

            current_status = task[1]

            if current_status != "PENDING_APPROVAL":
                return {
                    "error": f"Task cannot be rejected from status {current_status}"
                }, 400

            cursor.execute(
                """
                UPDATE tasks
                SET status = 'REJECTED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, status
                """,
                (task_id,)
            )

            updated_task = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    old_status,
                    new_status,
                    details
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    task_id,
                    user_id,
                    "TASK_REJECTED",
                    "PENDING_APPROVAL",
                    "REJECTED",
                    rejection_comment,
                )
            )

            cursor.execute(
                """
                INSERT INTO approvals (
                    task_id,
                    reviewed_by,
                    decision,
                    comment
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    task_id,
                    user_id,
                    "REJECTED",
                    rejection_comment,
                )
            )

        connection.commit()

        return {
            "message": "Task rejected successfully",
            "task": {
                "id": updated_task[0],
                "status": updated_task[1]
            },
            "rejection_comment": rejection_comment
        }, 200

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to reject task",
            "details": str(error)
        }, 500

    finally:
        connection.close()
@tasks_bp.put("/tasks/<int:task_id>/manage")
def manage_task(task_id):
    user_id = g.user_id

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, status
                FROM tasks
                WHERE id = %s
                  AND created_by = %s
                """,
                (task_id, user_id)
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to manage this task"
                }, 403

            current_status = task[1]

            if current_status != "PENDING":
                return {
                    "error": f"Task cannot be managed from status {current_status}"
                }, 400

            cursor.execute(
                """
                UPDATE tasks
                SET
                    status = 'MANAGED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, status
                """,
                (task_id,)
            )

            updated_task = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    old_status,
                    new_status,
                    details
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    task_id,
                    user_id,
                    "TASK_MANAGED",
                    "PENDING",
                    "MANAGED",
                    "Task managed by manager",
                )
            )

        connection.commit()

        return {
            "message": "Task managed successfully",
            "task": {
                "id": updated_task[0],
                "status": updated_task[1]
            }
        }, 200

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to manage task",
            "details": str(error)
        }, 500

    finally:
        connection.close()
@tasks_bp.put("/tasks/<int:task_id>/rework")
def rework_task(task_id):
    user_id = g.user_id
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, status
                FROM tasks
                WHERE id = %s
                  AND created_by = %s
                """,
                (task_id, user_id)
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to send this task for rework"
                }, 403

            current_status = task[1]

            if current_status != "REJECTED":
                return {
                    "error": f"Task cannot be sent for rework from status {current_status}"
                }, 400

            cursor.execute(
                """
                UPDATE tasks
                SET
                    status = 'MANAGED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, status
                """,
                (task_id,)
            )

            updated_task = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO task_history (
                    task_id,
                    user_id,
                    action,
                    old_status,
                    new_status,
                    details
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    task_id,
                    user_id,
                    "TASK_REWORKED",
                    "REJECTED",
                    "MANAGED",
                    "Task sent back for rework",
                )
            )

        connection.commit()

        return {
            "message": "Task sent for rework successfully",
            "task": {
                "id": updated_task[0],
                "status": updated_task[1]
            }
        }, 200

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to send task for rework",
            "details": str(error)
        }, 500

    finally:
        connection.close()



