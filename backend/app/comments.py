from flask import Blueprint, request, g
from app.db import get_db_connection


comments_bp = Blueprint("comments", __name__, url_prefix="/tasks")


@comments_bp.post("/<int:task_id>/comments")
def add_comment(task_id):
    user_id = g.user_id

    if not user_id:
        return {"error": "user_id is required"}, 400

    data = request.get_json(silent=True)

    if not data or not data.get("comment"):
        return {"error": "comment is required"}, 400

    comment_text = data["comment"].strip()

    if not comment_text:
        return {"error": "comment cannot be empty"}, 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM tasks
                WHERE id = %s
                  AND (created_by = %s OR assigned_to = %s)
                """,
                (task_id, user_id, user_id)
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to comment"
                }, 403

            cursor.execute(
                """
                INSERT INTO comments (task_id, user_id, comment)
                VALUES (%s, %s, %s)
                RETURNING id, task_id, user_id, comment, created_at, updated_at
                """,
                (task_id, user_id, comment_text)
            )

            new_comment = cursor.fetchone()

        connection.commit()

        return {
            "message": "Comment added successfully",
            "comment": {
                "id": new_comment[0],
                "task_id": new_comment[1],
                "user_id": new_comment[2],
                "comment": new_comment[3],
                "created_at": new_comment[4],
                "updated_at": new_comment[5]
            }
        }, 201

    except Exception as error:
        connection.rollback()

        return {
            "error": "Failed to add comment",
            "details": str(error)
        }, 500

    finally:
        connection.close()
@comments_bp.get("/<int:task_id>/comments")
def get_comments(task_id):
    user_id = g.user_id

    if not user_id:
        return {"error": "user_id is required"}, 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM tasks
                WHERE id = %s
                  AND (created_by = %s OR assigned_to = %s)
                """,
                (task_id, user_id, user_id)
            )

            task = cursor.fetchone()

            if not task:
                return {
                    "error": "Task not found or user is not authorized to view comments"
                }, 403

            cursor.execute(
                """
                SELECT id, task_id, user_id, comment, created_at, updated_at
                FROM comments
                WHERE task_id = %s
                ORDER BY created_at ASC
                """,
                (task_id,)
            )

            comments = cursor.fetchall()

        return {
            "task_id": task_id,
            "comments": [
                {
                    "id": row[0],
                    "task_id": row[1],
                    "user_id": row[2],
                    "comment": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                }
                for row in comments
            ]
        }, 200

    except Exception as error:
        return {
            "error": "Failed to retrieve comments",
            "details": str(error)
        }, 500

    finally:
        connection.close()