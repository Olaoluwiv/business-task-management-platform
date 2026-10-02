from flask import Flask, request
from flask_cors import CORS

from app.db import get_db_connection
from app.auth import require_authentication
from app.tasks import tasks_bp
from app.comments import comments_bp


def create_app():
    app = Flask(__name__)

    CORS(app)

    @app.before_request
    def authenticate_api_requests():
        if request.path in ["/health", "/db-health"]:
            return None

        return require_authentication()

    app.register_blueprint(tasks_bp)
    app.register_blueprint(comments_bp)

    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "service": "business-task-management-platform"
        }

    @app.get("/db-health")
    def db_health():
        try:
            connection = get_db_connection()

            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database();")
                database_name = cursor.fetchone()[0]

            connection.close()

            return {
                "status": "healthy",
                "database": database_name
            }

        except Exception as error:
            return {
                "status": "unhealthy",
                "error": str(error)
            }, 500

    return app