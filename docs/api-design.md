\# API Design



\## 1. Overview



The Business Task Management Platform exposes a REST API that allows employees and managers to manage tasks and follow the task approval workflow.



The backend API is responsible for:



\* Authentication and authorization

\* Task management

\* Role-based access control

\* Task status transitions

\* Task assignment

\* Approval and rejection

\* Comments

\* Task history



The frontend communicates with the backend through HTTPS requests.



\---



\## 2. API Base URL



Development:



```text

http://localhost:5000

```



Production:



```text

https://<api-domain>

```



\---



\## 3. Authentication



Authentication will eventually use Amazon Cognito.



The authenticated user will provide a Cognito access token with API requests.



The backend will determine:



\* User identity

\* User role

\* Permissions



Supported roles:



```text

EMPLOYEE

MANAGER

```



\---



\# 4. Task APIs



\## 4.1 Create Task



\### Endpoint



```http

POST /tasks

```



\### Permission



```text

MANAGER

```



Only managers can create tasks.



\### Request



```json

{

&#x20; "title": "Prepare monthly sales report",

&#x20; "description": "Prepare the September sales performance report.",

&#x20; "priority": "HIGH",

&#x20; "assigned\_to": 12,

&#x20; "due\_date": "2026-09-30T17:00:00Z"

}

```



\### Fields



| Field       | Required | Description                   |

| ----------- | -------- | ----------------------------- |

| title       | Yes      | Task title                    |

| description | Yes      | Task details                  |

| priority    | Yes      | LOW, MEDIUM, or HIGH          |

| assigned\_to | Yes      | Employee assigned to the task |

| due\_date    | No       | Task deadline                 |



\### Initial Status



New tasks start with:



```text

PENDING

```



\### Response



```json

{

&#x20; "id": 1,

&#x20; "title": "Prepare monthly sales report",

&#x20; "description": "Prepare the September sales performance report.",

&#x20; "priority": "HIGH",

&#x20; "status": "PENDING",

&#x20; "created\_by": 5,

&#x20; "assigned\_to": 12,

&#x20; "due\_date": "2026-09-30T17:00:00Z"

}

```



\### Status Codes



```text

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

500 Internal Server Error

```



\### History



Creating a task creates a task history record:



```text

TASK\_CREATED

```



\---



\# 5. Task Statuses



The platform uses the following task statuses:



```text

PENDING

IN\_PROGRESS

PENDING\_APPROVAL

APPROVED

COMPLETED

```



\### Status Flow



```text

PENDING

&#x20;  ↓

IN\_PROGRESS

&#x20;  ↓

PENDING\_APPROVAL

&#x20;  ↓

APPROVED

&#x20;  ↓

COMPLETED

```



\### Rejection Flow



```text

PENDING\_APPROVAL

&#x20;       ↓

&#x20;   REJECTED

&#x20;       ↓

&#x20;  IN\_PROGRESS

```



`REJECTED` is recorded as an approval decision and task-history event. It is not stored as the task's permanent status.



\---



\# 6. Role Rules



\## Employee



Employees can:



\* View assigned tasks

\* Start tasks

\* Update their tasks

\* Submit tasks for approval

\* Add comments

\* View task history

\* Rework rejected tasks



Employees cannot:



\* Create tasks

\* Assign tasks

\* Approve tasks

\* Reject tasks



\## Manager



Managers can:



\* Create tasks

\* Assign tasks

\* Reassign tasks

\* View team tasks

\* Update/manage tasks

\* Add comments

\* Review submitted tasks

\* Approve tasks

\* Reject tasks

\* View task history



\---



\# 7. Error Response Format



The API will use a consistent error format.



Example:



```json

{

&#x20; "error": "Task cannot be approved",

&#x20; "message": "Task must be in PENDING\_APPROVAL status."

}

```



This makes errors predictable for the frontend.



\---



\# 8. API Development Plan



The remaining task APIs will be documented before backend implementation begins.



Planned endpoints:



```text

GET    /tasks

GET    /tasks/{id}

PUT    /tasks/{id}

POST   /tasks/{id}/start

POST   /tasks/{id}/submit

POST   /tasks/{id}/approve

POST   /tasks/{id}/reject

POST   /tasks/{id}/comments

GET    /tasks/{id}/history

```



The API design will be finalized before Flask development begins.



