# 🔐 InstaSafe — Secure Authentication & Role-Based Access Control System

InstaSafe is a Flask-based REST API project that demonstrates secure user authentication, JWT-based authorization, password hashing, and Role-Based Access Control (RBAC).

The project was developed to understand practical backend security concepts commonly used in SaaS and web applications.

---

## 🚀 Features

* User registration
* Secure password hashing using bcrypt
* User login
* JWT-based authentication
* Protected API endpoints
* Role-Based Access Control (RBAC)
* Admin-only user management APIs
* User role management
* MySQL database integration
* Parameterized SQL queries
* Environment-based configuration
* API testing using Postman

---

## 🛠️ Tech Stack

| Technology         | Purpose                         |
| ------------------ | ------------------------------- |
| Python             | Programming language            |
| Flask              | REST API framework              |
| MySQL              | Database                        |
| PyMySQL            | MySQL database connectivity     |
| Flask-Bcrypt       | Password hashing                |
| Flask-JWT-Extended | JWT authentication              |
| Postman            | API testing                     |
| python-dotenv      | Environment variable management |
| Git & GitHub       | Version control                 |

---

# 🏗️ Project Architecture

```text
                    Client / Postman
                           │
                           ▼
                    Flask REST API
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          Register       Login      Protected APIs
              │            │            │
              ▼            ▼            ▼
           bcrypt       bcrypt       JWT Validation
              │            │            │
              └────────────┴────────────┤
                                        ▼
                                   Role Checking
                                        │
                              ┌─────────┴─────────┐
                              │                   │
                            USER                ADMIN
                              │                   │
                         Access Denied         Allowed
                              │                   │
                            403                  200
                                                  │
                                                  ▼
                                                MySQL
```

---

# 🔐 Authentication Flow

The application uses bcrypt and JWT to implement authentication.

```text
User
 │
 │ Register
 ▼
Flask API
 │
 ▼
Password hashed using bcrypt
 │
 ▼
Stored in MySQL
```

During login:

```text
Username + Password
        │
        ▼
     Flask API
        │
        ▼
Find user in MySQL
        │
        ▼
Verify password using bcrypt
        │
   ┌────┴────┐
   │         │
 Wrong     Correct
   │         │
  401       JWT
             │
             ▼
        Access Token
```

---

# 🎟️ JWT Authentication

After successful login, the server generates a JWT access token.

The token contains information such as:

* User ID
* Username
* Role
* Token metadata
* Expiration time

The client sends the token when accessing protected endpoints:

```text
Authorization: Bearer <JWT>
```

The server validates the JWT before allowing access to protected resources.

---

# 👥 Role-Based Access Control

The application implements two roles:

```text
USER
ADMIN
```

The role is included in the JWT claims and checked when accessing administrative APIs.

### Standard User

```text
testuser
   │
   ▼
GET /admin/users
   │
   ▼
403 Forbidden
```

### Administrator

```text
nitish
   │
   ▼
GET /admin/users
   │
   ▼
200 OK
```

This demonstrates the difference between authentication and authorization.

> **Authentication:** Who are you?

> **Authorization:** What are you allowed to access?

---

# 🛡️ RBAC Implementation

A reusable `admin_required()` decorator is used to protect administrator-only endpoints.

The authorization flow is:

```text
Request
   │
   ▼
JWT present?
   │
   ▼
JWT valid?
   │
   ▼
Read role claim
   │
   ▼
role == admin?
   │
 ┌─┴─────────┐
 │           │
YES          NO
 │           │
 ▼           ▼
Allow       403
request     Forbidden
```

This keeps authorization logic reusable instead of duplicating role checks inside every administrative route.

---

# 🔑 Password Security

Passwords are never stored as plaintext.

For example, the user enters:

```text
TestPassword123
```

The application generates a bcrypt hash before storing it in MySQL.

Conceptually:

```text
Plaintext Password
       │
       ▼
     bcrypt
       │
       ▼
Password Hash
       │
       ▼
     MySQL
```

During login, the supplied password is verified against the stored bcrypt hash.

Bcrypt is an adaptive password hashing algorithm with per-password salts, making password cracking more computationally expensive than using a simple fast hash.

---

# 🗄️ Database

MySQL is used to store user information.

The users table contains information such as:

```text
+----+----------+-------+
| id | username | role  |
+----+----------+-------+
| 1  | nitish   | admin |
| 2  | testuser | user  |
+----+----------+-------+
```

Passwords are stored as bcrypt hashes rather than plaintext passwords.

---

# 🔒 SQL Injection Protection

Database queries use parameterized SQL statements.

Example:

```python
cursor.execute(
    "SELECT id FROM users WHERE username = %s",
    (username,)
)
```

Instead of directly concatenating user input into SQL statements.

This helps reduce the risk of SQL injection.

---

# 🌱 Environment Variables

Sensitive configuration is stored in a `.env` file rather than directly inside the source code.

Example:

```env
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=auth_system
```

The `.env` file is excluded from Git using `.gitignore`.

A `.env.example` file is provided so that another developer can understand which environment variables are required.

> Never commit real passwords, secret keys, database credentials, or JWT secrets to GitHub.

---

# 🔑 Token Handling

The project uses JWT access tokens for authentication.

### Token lifetime

Access tokens are configured with an expiration time by Flask-JWT-Extended.

### Refresh tokens

Refresh tokens are **not implemented** in the current version of this project.

### Token storage

This project is a REST API demonstrated and tested using Postman. The JWT is returned to the client after successful login and supplied as a Bearer token when accessing protected APIs.

### Invalid or expired tokens

Protected endpoints validate the JWT before processing the request.

Invalid, missing, expired, or improperly signed tokens are rejected by the JWT authentication layer.

---

# 📡 API Endpoints

## 1. Home

```http
GET /
```

Returns a message confirming that the application is running.

---

## 2. Register

```http
POST /register
```

### Request

```json
{
    "username": "testuser",
    "password": "TestPassword123"
}
```

### Successful response

```json
{
    "message": "User registered successfully"
}
```

---

## 3. Login

```http
POST /login
```

### Request

```json
{
    "username": "nitish",
    "password": "TestPassword123"
}
```

### Successful response

```json
{
    "message": "Login successful",
    "access_token": "<JWT_TOKEN>",
    "user": {
        "id": 1,
        "username": "nitish",
        "role": "admin"
    }
}
```

---

## 4. Protected Profile

```http
GET /profile
```

Requires:

```text
Authorization: Bearer <JWT_TOKEN>
```

A valid JWT is required to access the endpoint.

---

## 5. Get All Users — Admin Only

```http
GET /admin/users
```

Requires a valid JWT belonging to an administrator.

### Admin response

```json
{
    "message": "Admin access granted",
    "users": [
        {
            "id": 1,
            "role": "admin",
            "username": "nitish"
        },
        {
            "id": 2,
            "role": "user",
            "username": "testuser"
        }
    ]
}
```

A normal user receives:

```json
{
    "message": "Admin access required"
}
```

with:

```text
403 Forbidden
```

---

## 6. Update User Role — Admin Only

```http
PUT /admin/users/<user_id>/role
```

### Request

```json
{
    "role": "admin"
}
```

Only an authenticated administrator can perform this operation.

---

# 🧪 API Testing

The APIs were tested using Postman.

Important test cases include:

| Test Case                 | Expected Result    |
| ------------------------- | ------------------ |
| Valid registration        | `201 Created`      |
| Duplicate username        | `409 Conflict`     |
| Missing registration data | `400 Bad Request`  |
| Valid login               | `200 OK`           |
| Invalid login             | `401 Unauthorized` |
| Protected API without JWT | `401 Unauthorized` |
| Valid JWT                 | Access granted     |
| User accessing admin API  | `403 Forbidden`    |
| Admin accessing admin API | `200 OK`           |
| Admin role update         | Successful         |
| Invalid/modified JWT      | Request rejected   |

---

# 🔄 Example RBAC Scenario

The project was tested using two users:

```text
nitish
Role: admin
```

and:

```text
testuser
Role: user
```

### Admin

```text
Login
  ↓
JWT generated
  ↓
GET /admin/users
  ↓
Role = admin
  ↓
200 OK
```

### Normal User

```text
Login
  ↓
JWT generated
  ↓
GET /admin/users
  ↓
Role = user
  ↓
403 Forbidden
```

This confirms that authentication alone is not enough to access administrative resources.

---

# 📁 Project Structure

```text
InstaSafe-Auth-System/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── .env
└── venv/
```

### Files not uploaded to GitHub

```text
.env
venv/
__pycache__/
```

These are excluded using `.gitignore`.

---

# ⚙️ Installation & Setup

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/InstaSafe-Auth-System.git
```

```bash
cd InstaSafe-Auth-System
```

---

## 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file in the project root.

```env
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=auth_system
```

---

## 5. Create the MySQL database

Create the database:

```sql
CREATE DATABASE auth_system;
```

Create the users table:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);
```

---

## 6. Run the application

```bash
python app.py
```

The API will run at:

```text
http://127.0.0.1:5000
```

---

# 📌 Learning Outcomes

Through this project, I gained practical experience with:

* REST API development using Flask
* Authentication and authorization
* JWT-based authentication
* Password hashing with bcrypt
* Role-Based Access Control
* Protected API endpoints
* MySQL database integration
* Parameterized SQL queries
* Environment variable management
* API testing with Postman
* Git and GitHub
* Basic SaaS security concepts

---

# 🔮 Future Improvements

Possible improvements for future versions include:

* Refresh token implementation
* Token revocation / logout mechanism
* More granular permissions
* Password reset functionality
* Email verification
* Rate limiting for login attempts
* Account lockout after repeated failures
* Security logging and audit trails
* Automated unit and integration tests
* Docker containerization
* Cloud deployment
* HTTPS configuration
* CI/CD pipeline

---

# 🎯 Project Goal

The goal of InstaSafe is to demonstrate how authentication, authorization, password security, database security, and RBAC can be combined to create a more secure backend API.

The project focuses on understanding the security flow rather than building a large production application.

---

## 👨‍💻 Author

**Nitish Pale**

B.E. Electronics & Telecommunication Engineering

Skills demonstrated through this project:

**Python • Flask • MySQL • REST APIs • JWT • RBAC • Bcrypt • Postman • Git/GitHub**

---

## ⭐ Acknowledgements

This project was developed as a hands-on learning project to understand practical backend authentication and application security concepts.
