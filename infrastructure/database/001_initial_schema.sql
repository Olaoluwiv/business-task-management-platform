CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    cognito_user_id VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT users_role_check
        CHECK (role IN ('EMPLOYEE', 'MANAGER'))
);


CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_by BIGINT NOT NULL,
    assigned_to BIGINT,
    due_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT tasks_priority_check
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),

    CONSTRAINT tasks_status_check
        CHECK (
            status IN (
                'PENDING',
                'MANAGED',
                'IN_PROGRESS',
                'PENDING_APPROVAL',
                'APPROVED',
                'REJECTED',
                'COMPLETED'
            )
        ),

    CONSTRAINT tasks_created_by_fk
        FOREIGN KEY (created_by)
        REFERENCES users(id),

    CONSTRAINT tasks_assigned_to_fk
        FOREIGN KEY (assigned_to)
        REFERENCES users(id)
);


CREATE TABLE task_history (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT task_history_task_fk
        FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE,

    CONSTRAINT task_history_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);


CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT comments_task_fk
        FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE,

    CONSTRAINT comments_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);


CREATE TABLE approvals (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL,
    reviewed_by BIGINT NOT NULL,
    decision VARCHAR(20) NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT approvals_decision_check
        CHECK (decision IN ('APPROVED', 'REJECTED')),

    CONSTRAINT approvals_task_fk
        FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE,

    CONSTRAINT approvals_reviewer_fk
        FOREIGN KEY (reviewed_by)
        REFERENCES users(id)
);