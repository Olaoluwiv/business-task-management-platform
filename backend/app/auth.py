import os
from functools import wraps
from app.db import get_db_connection

import jwt
from jwt import PyJWKClient
from flask import request, jsonify, g


COGNITO_REGION = os.getenv(
    "COGNITO_REGION",
    "us-east-1"
)

COGNITO_USER_POOL_ID = os.getenv(
    "COGNITO_USER_POOL_ID",
    "us-east-1_d456zIN4H"
)

COGNITO_APP_CLIENT_ID = os.getenv(
    "COGNITO_APP_CLIENT_ID",
    "2pkuov30f6mq0lm8o9kologsko"
)

COGNITO_ISSUER = (
    f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/"
    f"{COGNITO_USER_POOL_ID}"
)

COGNITO_JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

jwks_client = PyJWKClient(COGNITO_JWKS_URL)


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    return auth_header.split(" ", 1)[1]


def require_authentication():
    token = get_bearer_token()

    if not token:
        return jsonify({
            "error": "Authentication token is required"
        }), 401

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=COGNITO_ISSUER,
            options={
                "verify_exp": True
            }
        )

        if payload.get("token_use") != "access":
            return jsonify({
                "error": "Invalid token type"
            }), 401

        if payload.get("client_id") != COGNITO_APP_CLIENT_ID:
            return jsonify({
                "error": "Invalid client"
            }), 401

        cognito_user_id = payload.get("sub")

        if not cognito_user_id:
            return jsonify({
                "error": "Invalid authentication token"
            }), 401

        g.cognito_user_id = cognito_user_id
        connection = get_db_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, role
                    FROM users
                    WHERE cognito_user_id = %s
                    """,
                    (cognito_user_id,)
                )

                user = cursor.fetchone()

            if not user:
                return jsonify({
                    "error": "Authenticated user is not registered"
                }), 403

            g.user_id = user[0]
            g.user_role = user[1]

        finally:
            connection.close()

        return None

    except jwt.ExpiredSignatureError:
        return jsonify({
            "error": "Authentication token has expired"
        }), 401

    except jwt.InvalidTokenError as error:
        print(
            f"JWT validation error: "
            f"{type(error).__name__}: {error}",
            flush=True
        )
        return jsonify({
            "error": "Invalid authentication token"
        }), 401

    except Exception as error:
        print(
            f"Authentication error: "
            f"{type(error).__name__}: {error}",
            flush=True
        )
        return jsonify({
            "error": "Authentication failed"
        }), 401