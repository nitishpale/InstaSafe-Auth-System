from flask import Flask, request, jsonify
from config import Config
import pymysql
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from functools import wraps


# =================================
# FLASK APPLICATION
# =================================

app = Flask(__name__)
app.config.from_object(Config)


# =================================
# SECURITY TOOLS
# =================================

bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# =================================
# DATABASE CONNECTION
# =================================

def get_db_connection():
    return pymysql.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
        cursorclass=pymysql.cursors.DictCursor
    )


# =================================
# ADMIN ROLE CHECK / RBAC
# =================================

def admin_required():
    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            if claims.get("role") != "admin":
                return jsonify({
                    "message": "Admin access required"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator


# =================================
# HOME
# =================================

@app.route("/")
def home():

    return "Secure Authentication & RBAC System is running!"


# =================================
# REGISTER
# =================================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    username = data.get("username")
    password = data.get("password")

    # Validate username and password
    if not username or not password:
        return jsonify({
            "message": "Username and password are required"
        }), 400

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            # Check whether username already exists
            cursor.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({
                    "message": "Username already exists"
                }), 409

            # Hash password using bcrypt
            hashed_password = bcrypt.generate_password_hash(
                password
            ).decode("utf-8")

            # Create normal user
            cursor.execute(
                """
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
                """,
                (
                    username,
                    hashed_password,
                    "user"
                )
            )

            connection.commit()

        return jsonify({
            "message": "User registered successfully"
        }), 201

    finally:

        connection.close()


# =================================
# LOGIN
# =================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    username = data.get("username")
    password = data.get("password")

    # Validate input
    if not username or not password:
        return jsonify({
            "message": "Username and password are required"
        }), 400

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            # Find user
            cursor.execute(
                """
                SELECT id, username, password, role
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

            # User doesn't exist
            if not user:
                return jsonify({
                    "message": "Invalid username or password"
                }), 401

            # Check password
            password_valid = bcrypt.check_password_hash(
                user["password"],
                password
            )

            # Wrong password
            if not password_valid:
                return jsonify({
                    "message": "Invalid username or password"
                }), 401

            # =================================
            # CREATE JWT TOKEN
            # =================================

            access_token = create_access_token(
                identity=str(user["id"]),
                additional_claims={
                    "username": user["username"],
                    "role": user["role"]
                }
            )

            return jsonify({

                "message": "Login successful",

                "access_token": access_token,

                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "role": user["role"]
                }

            }), 200

    finally:

        connection.close()


# =================================
# PROTECTED PROFILE API
# =================================

@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    # Get user ID from JWT
    current_user_id = get_jwt_identity()

    # Get additional claims from JWT
    claims = get_jwt()

    return jsonify({

        "message": "Access granted",

        "user_id": current_user_id,

        "username": claims.get("username"),

        "role": claims.get("role")

    }), 200


# =================================
# ADMIN - GET ALL USERS
# =================================

@app.route("/admin/users", methods=["GET"])
@admin_required()
def admin_users():

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            # Get users WITHOUT passwords
            cursor.execute(
                """
                SELECT id, username, role
                FROM users
                """
            )

            users = cursor.fetchall()

        return jsonify({

            "message": "Admin access granted",

            "users": users

        }), 200

    finally:

        connection.close()

# =================================
# ADMIN - UPDATE USER ROLE
# =================================

@app.route("/admin/users/<int:user_id>/role", methods=["PUT"])
@admin_required()
def update_user_role(user_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    new_role = data.get("role")

    if new_role not in ["user", "admin"]:
        return jsonify({
            "message": "Role must be either user or admin"
        }), 400

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            # Check user exists
            cursor.execute(
                """
                SELECT id, username, role
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            if not user:
                return jsonify({
                    "message": "User not found"
                }), 404

            # Update role
            cursor.execute(
                """
                UPDATE users
                SET role = %s
                WHERE id = %s
                """,
                (new_role, user_id)
            )

            connection.commit()

        return jsonify({
            "message": "User role updated successfully",
            "user_id": user_id,
            "username": user["username"],
            "new_role": new_role
        }), 200

    finally:

        connection.close()

# =================================
# HEALTH CHECK
# =================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "service": "InstaSafe Authentication API"
    }), 200


# =================================
# RUN APPLICATION
# =================================

if __name__ == "__main__":

    app.run(debug=True)
