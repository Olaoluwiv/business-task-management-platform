# Business Task Management Platform

A full-stack task management platform designed to manage business work from task creation and assignment through execution, review, approval, rejection, and rework.

## Overview

The Business Task Management Platform provides separate workflows for **Managers** and **Employees**.

### Manager

Managers can:

* Create tasks
* Assign tasks to employees
* Manage tasks
* Review submitted work
* Approve completed work
* Reject work with a reason
* Return rejected work for rework

### Employee

Employees can:

* Sign in securely
* View assigned tasks
* Start managed tasks
* Update task information
* Complete tasks and submit them for approval
* View approved or rejected tasks
* Continue work on rejected tasks after rework

---

## Task Workflow

### Normal workflow

```text
PENDING
   ↓
MANAGED
   ↓
IN_PROGRESS
   ↓
PENDING_APPROVAL
   ↓
APPROVED
```

### Rejection and rework workflow

```text
PENDING_APPROVAL
   ↓
REJECTED
   ↓
MANAGED
   ↓
IN_PROGRESS
   ↓
PENDING_APPROVAL
   ↓
APPROVED
```

The application also maintains task history so important workflow changes can be audited.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │ Employee / Manager   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ HTML / CSS / JS      │
                    │ Frontend             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Application Load     │
                    │ Balancer             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ AWS ECS / Fargate     │
                    │ Flask REST API        │
                    └───────┬───────┬──────┘
                            │       │
                ┌───────────┘       └────────────┐
                ▼                                ▼
       ┌─────────────────┐              ┌─────────────────┐
       │ Amazon Cognito  │              │ PostgreSQL      │
       │ Authentication  │              │ Task Database   │
       └─────────────────┘              └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │ AWS Secrets     │
       │ Manager         │
       └─────────────────┘
```

---

## Technology Stack

| Component          | Technology                |
| ------------------ | ------------------------- |
| Frontend           | HTML, CSS, JavaScript     |
| Backend            | Python / Flask            |
| Database           | PostgreSQL                |
| Local Database     | Docker                    |
| Authentication     | Amazon Cognito            |
| JWT Validation     | PyJWT + cryptography      |
| Containerization   | Docker                    |
| Container Registry | Amazon ECR                |
| Cloud Compute      | Amazon ECS / Fargate      |
| Load Balancing     | Application Load Balancer |
| Secrets            | AWS Secrets Manager       |
| Networking         | Amazon VPC                |
| Testing            | pytest + API testing      |
| Version Control    | Git / GitHub              |

---

## Backend API

The Flask backend provides endpoints for:

```text
GET    /health
GET    /db-health

GET    /tasks
POST   /tasks
GET    /tasks/<id>
PUT    /tasks/<id>

PUT    /tasks/<id>/manage
PUT    /tasks/<id>/start
PUT    /tasks/<id>/complete
PUT    /tasks/<id>/approve
PUT    /tasks/<id>/reject
PUT    /tasks/<id>/rework

GET    /tasks/<id>/comments
POST   /tasks/<id>/comments
```

Protected endpoints require a Cognito access token.

---

## Authentication and Authorization

Amazon Cognito is used for user authentication.

The backend validates:

* JWT signature
* Cognito issuer
* token expiry
* token type
* Cognito app client
* Cognito user identity

The Cognito `sub` is then mapped to a local application user in PostgreSQL.

The backend uses the authenticated identity stored in the request context rather than trusting a client-provided `user_id`.

This allows authorization rules to be enforced on the server.

---

## Database

The PostgreSQL database contains core entities including:

* `users`
* `tasks`
* `task_history`
* `approvals`
* comments

The `task_history` table provides an audit trail for workflow changes.

Example events include:

```text
TASK_CREATED
TASK_MANAGED
TASK_STARTED
TASK_COMPLETED
TASK_APPROVED
TASK_REJECTED
TASK_REWORKED
```

---

## Testing

Several complete workflows were tested.

### Successful task lifecycle

Task 13 completed:

```text
PENDING
→ MANAGED
→ IN_PROGRESS
→ PENDING_APPROVAL
→ APPROVED
```

### Rejection and rework

Task 14 completed:

```text
PENDING_APPROVAL
→ REJECTED
→ MANAGED
→ IN_PROGRESS
→ PENDING_APPROVAL
→ APPROVED
```

### Authorization testing

Manager-only operations were tested against employee accounts, including:

* Manage
* Approve
* Reject

Unauthorized operations were rejected by the backend.

---

## AWS Deployment

The application was deployed using:

* Amazon ECR
* Amazon ECS/Fargate
* Application Load Balancer
* Amazon Cognito
* AWS Secrets Manager
* Amazon VPC
* NAT Gateway
* Security Groups

The backend was containerized and deployed to ECS.

During deployment, an authentication problem was traced to the Docker image missing the `cryptography` dependency required for RS256 JWT validation.

The dependency was added to the backend requirements, the Docker image was rebuilt, pushed to ECR, and deployed as a new ECS task-definition revision.

The subsequent authentication test successfully progressed through JWT validation and reached the application-user lookup.

---

## Current Project Status

The core application and deployment workflow have been implemented and tested.

The current AWS resume point is:

```text
Cognito authentication
        ↓
JWT validation
        ↓
Cognito user lookup
        ↓
Application user mapping
```

The remaining authentication issue is that the Cognito user's `sub` has not yet been registered in the application's PostgreSQL `users.cognito_user_id` field.

This is the next development task when the project is resumed.

AWS resources can be paused while development continues locally to avoid unnecessary cloud costs.

---

## Local Development

### Start PostgreSQL

```powershell
docker compose up -d
```

### Start the backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python run.py
```

Backend:

```text
http://127.0.0.1:8000
```

### Start the frontend

```powershell
cd frontend
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500/login.html
```

---

## Project Structure

```text
business-task-management-platform/
│
├── backend/
│   ├── app/
│   │   ├── auth.py
│   │   ├── comments.py
│   │   ├── db.py
│   │   └── tasks.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   ├── login.html
│   ├── login.js
│   └── style.css
│
├── infrastructure/
│   └── database/
│
├── docs/
│   ├── api-design.md
│   ├── database-design.md
│   └── project-report.md
│
├── tests/
│
├── docker-compose.yml
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Future Improvements

Planned improvements include:

* Complete Cognito user registration/mapping
* HTTPS configuration
* Production CORS configuration
* Role-specific dashboard views
* Logout and session handling
* Improved frontend task filtering
* More automated integration tests
* GitHub Actions CI/CD
* AWS OIDC deployment
* Infrastructure as Code
* Monitoring and alerting

---

## Project Report

A detailed project report covering the architecture, implementation, AWS deployment, authentication, testing, challenges, and future improvements is available in:

`docs/project-report.md`

---

## Security

Secrets and passwords should never be committed to Git.

The project uses environment variables and AWS Secrets Manager for sensitive configuration.

Temporary deployment files and local secret files are excluded through `.gitignore`.

---

## Status

**Development milestone completed**

The platform has a working backend, PostgreSQL database, authentication integration, frontend, Docker configuration, automated tests, and AWS deployment.

The project is currently paused on AWS to control cloud costs and can be resumed from the documented authentication-user-mapping step.
