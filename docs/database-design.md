\# Business Task Management Platform — Database Design



\## 1. Overview



The Business Task Management Platform will use PostgreSQL as its relational database.



In the AWS environment, PostgreSQL will run on Amazon RDS inside private subnets.



The database will store:



\* Users

\* Tasks

\* Task history

\* Comments

\* Approval decisions



The database is designed for Version 1 of the application.



\---



\## 2. Database Tables



Version 1 contains five core tables:



```text

users

tasks

task\_history

comments

approvals

```



Relationship overview:



```text

users

&#x20; │

&#x20; ├───────────────┐

&#x20; │               │

&#x20; ▼               ▼

tasks          approvals

&#x20; │

&#x20; ├──────────────┐

&#x20; │              │

&#x20; ▼              ▼

comments     task\_history

```



\---



\## 3. Users Table



The `users` table represents application users.



\### Columns



| Column          | Type         | Constraints      | Description                    |

| --------------- | ------------ | ---------------- | ------------------------------ |

| id              | BIGSERIAL    | PRIMARY KEY      | Internal user identifier       |

| cognito\_user\_id | VARCHAR(255) | UNIQUE, NOT NULL | Amazon Cognito user identifier |

| first\_name      | VARCHAR(100) | NOT NULL         | User first name                |

| last\_name       | VARCHAR(100) | NOT NULL         | User last name                 |

| email           | VARCHAR(255) | UNIQUE, NOT NULL | User email address             |

| role            | VARCHAR(20)  | NOT NULL         | Employee or Manager            |

| created\_at      | TIMESTAMPTZ  | NOT NULL         | Account creation time          |

| updated\_at      | TIMESTAMPTZ  | NOT NULL         | Last update time               |



\### Allowed roles



```text

EMPLOYEE

MANAGER

```



\---



\## 4. Tasks Table



The `tasks` table stores the current state of every business task.



\### Columns



| Column      | Type         | Constraints | Description                  |

| ----------- | ------------ | ----------- | ---------------------------- |

| id          | BIGSERIAL    | PRIMARY KEY | Task identifier              |

| title       | VARCHAR(200) | NOT NULL    | Task title                   |

| description | TEXT         | NOT NULL    | Task description             |

| priority    | VARCHAR(20)  | NOT NULL    | Task priority                |

| status      | VARCHAR(30)  | NOT NULL    | Current task status          |

| created\_by  | BIGINT       | FOREIGN KEY | Manager who created the task |

| assigned\_to | BIGINT       | FOREIGN KEY | Employee currently assigned  |

| due\_date    | TIMESTAMPTZ  | NULL        | Task deadline                |

| created\_at  | TIMESTAMPTZ  | NOT NULL    | Creation time                |

| updated\_at  | TIMESTAMPTZ  | NOT NULL    | Last update time             |



\### Allowed priorities



```text

LOW

MEDIUM

HIGH

```



\### Allowed statuses



```text

PENDING

IN\_PROGRESS

PENDING\_APPROVAL

APPROVED

COMPLETED

```



`REJECTED` is not stored as a permanent task status.



When a manager rejects a task:



```text

PENDING\_APPROVAL

&#x20;       ↓

&#x20;     REJECT

&#x20;       ↓

IN\_PROGRESS

```



The rejection itself is recorded in the `approvals` and `task\_history` tables.



\---



\## 5. Task History Table



The `task\_history` table provides an audit trail of important task activity.



\### Columns



| Column     | Type        | Constraints           | Description                   |

| ---------- | ----------- | --------------------- | ----------------------------- |

| id         | BIGSERIAL   | PRIMARY KEY           | History record identifier     |

| task\_id    | BIGINT      | FOREIGN KEY, NOT NULL | Related task                  |

| user\_id    | BIGINT      | FOREIGN KEY, NOT NULL | User who performed the action |

| action     | VARCHAR(50) | NOT NULL              | Action performed              |

| old\_status | VARCHAR(30) | NULL                  | Previous task status          |

| new\_status | VARCHAR(30) | NULL                  | New task status               |

| details    | TEXT        | NULL                  | Additional information        |

| created\_at | TIMESTAMPTZ | NOT NULL              | Time of the event             |



\### Example actions



```text

TASK\_CREATED

TASK\_ASSIGNED

TASK\_REASSIGNED

TASK\_STARTED

TASK\_UPDATED

TASK\_SUBMITTED

TASK\_APPROVED

TASK\_REJECTED

TASK\_COMPLETED

```



Example:



```text

Task: 15

User: 7

Action: TASK\_SUBMITTED

Old Status: IN\_PROGRESS

New Status: PENDING\_APPROVAL

Details: Employee submitted completed work

```



\---



\## 6. Comments Table



The `comments` table stores communication associated with a task.



\### Columns



| Column     | Type        | Constraints           | Description                  |

| ---------- | ----------- | --------------------- | ---------------------------- |

| id         | BIGSERIAL   | PRIMARY KEY           | Comment identifier           |

| task\_id    | BIGINT      | FOREIGN KEY, NOT NULL | Related task                 |

| user\_id    | BIGINT      | FOREIGN KEY, NOT NULL | User who created the comment |

| comment    | TEXT        | NOT NULL              | Comment content              |

| created\_at | TIMESTAMPTZ | NOT NULL              | Creation time                |

| updated\_at | TIMESTAMPTZ | NOT NULL              | Last update time             |



Example:



```text

Manager:

"Please correct the customer reference before resubmitting."

```



\---



\## 7. Approvals Table



The `approvals` table records manager approval decisions.



\### Columns



| Column      | Type        | Constraints           | Description                   |

| ----------- | ----------- | --------------------- | ----------------------------- |

| id          | BIGSERIAL   | PRIMARY KEY           | Approval record identifier    |

| task\_id     | BIGINT      | FOREIGN KEY, NOT NULL | Related task                  |

| reviewed\_by | BIGINT      | FOREIGN KEY, NOT NULL | Manager who reviewed the task |

| decision    | VARCHAR(20) | NOT NULL              | Approval decision             |

| comment     | TEXT        | NULL                  | Review comment                |

| created\_at  | TIMESTAMPTZ | NOT NULL              | Review time                   |



\### Allowed decisions



```text

APPROVED

REJECTED

```



A task can have multiple approval records because a rejected task can be corrected and submitted again.



\---



\## 8. Relationships



\### Users → Tasks



A manager can create multiple tasks.



```text

users.id

&#x20;   │

&#x20;   └── tasks.created\_by

```



An employee can be assigned multiple tasks.



```text

users.id

&#x20;   │

&#x20;   └── tasks.assigned\_to

```



\---



\### Tasks → Task History



One task can have many history records.



```text

tasks.id

&#x20;   │

&#x20;   └── task\_history.task\_id

```



\---



\### Tasks → Comments



One task can have many comments.



```text

tasks.id

&#x20;   │

&#x20;   └── comments.task\_id

```



\---



\### Tasks → Approvals



One task can have multiple approval records.



```text

tasks.id

&#x20;   │

&#x20;   └── approvals.task\_id

```



\---



\## 9. Foreign Key Relationships



```text

tasks.created\_by

&#x20;   → users.id



tasks.assigned\_to

&#x20;   → users.id



task\_history.task\_id

&#x20;   → tasks.id



task\_history.user\_id

&#x20;   → users.id



comments.task\_id

&#x20;   → tasks.id



comments.user\_id

&#x20;   → users.id



approvals.task\_id

&#x20;   → tasks.id



approvals.reviewed\_by

&#x20;   → users.id

```



\---



\## 10. Task Lifecycle



The normal workflow is:



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



Rejected work follows:



```text

PENDING\_APPROVAL

&#x20;      │

&#x20;      ▼

&#x20;  REJECTED

&#x20;      │

&#x20;      ▼

IN\_PROGRESS

```



`REJECTED` represents an action/decision recorded in the approval and history records. The task itself returns to `IN\_PROGRESS`.



\---



\## 11. Task Permission Rules



\### Employee



Employees can:



\* View tasks assigned to them

\* Start assigned tasks

\* Update assigned tasks

\* Submit tasks for approval

\* View their task history

\* Add comments

\* Rework rejected tasks



Employees cannot:



\* Create team tasks

\* Assign tasks

\* Reassign tasks

\* Approve tasks

\* Reject tasks



\### Manager



Managers can:



\* Create tasks

\* Assign tasks

\* Reassign tasks

\* View team tasks

\* Update/manage tasks

\* Review submitted work

\* Approve tasks

\* Reject tasks

\* Add comments

\* View task history



\---



\## 12. Audit Trail



Important business actions should create a record in `task\_history`.



For example:



```text

Manager creates task

&#x20;       ↓

TASK\_CREATED



Manager assigns employee

&#x20;       ↓

TASK\_ASSIGNED



Employee starts work

&#x20;       ↓

TASK\_STARTED



Employee submits work

&#x20;       ↓

TASK\_SUBMITTED



Manager rejects

&#x20;       ↓

TASK\_REJECTED



Employee resubmits

&#x20;       ↓

TASK\_SUBMITTED



Manager approves

&#x20;       ↓

TASK\_APPROVED



Task completed

&#x20;       ↓

TASK\_COMPLETED

```



This provides accountability without storing historical information directly inside the `tasks` table.



\---



\## 13. Database Security



In the AWS environment:



```text

Internet

&#x20;  │

&#x20;  X

&#x20;  │

&#x20;  │ No direct database access

&#x20;  ▼

RDS PostgreSQL

```



The RDS database will:



\* Run inside private subnets

\* Not have a public IP

\* Accept PostgreSQL connections only from the application layer

\* Use security groups to restrict access

\* Store credentials in AWS Secrets Manager

\* Be accessed by the backend through its ECS task role



Database credentials must never be committed to GitHub.



\---



\## 14. Version 1 Scope



The following are intentionally excluded from the Version 1 database:



\* Multi-tenancy

\* Organizations

\* Departments

\* Notifications

\* File attachments

\* Chat

\* Advanced reporting

\* Administrator accounts

\* Soft-delete framework

\* Complex event sourcing



These can be considered for future versions after the core platform is working.



\---



\## 15. Database Architecture



The final AWS database architecture will be:



```text

&#x20;                   AWS VPC

&#x20;                      │

&#x20;               Private Subnets

&#x20;                      │

&#x20;             ┌────────┴────────┐

&#x20;             │                 │

&#x20;             ▼                 ▼

&#x20;       ECS Fargate          RDS PostgreSQL

&#x20;       Backend API              │

&#x20;             │                  │

&#x20;             └───────SQL────────┘

```



The backend application is the only application component that should communicate directly with PostgreSQL.



