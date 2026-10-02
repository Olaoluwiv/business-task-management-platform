const API_URL =
    "http://business-task-management-alb-952744492.us-east-1.elb.amazonaws.com";

const ACCESS_TOKEN =
    localStorage.getItem("access_token");

function authHeaders() {
    return {
        "Authorization": `Bearer ${ACCESS_TOKEN}`
    };
}
function formatTaskStatus(status) {
    const statusLabels = {
        PENDING: "Pending",
        MANAGED: "Managed",
        IN_PROGRESS: "In Progress",
        PENDING_APPROVAL: "Awaiting Approval",
        APPROVED: "Approved",
        REJECTED: "Rejected",
        COMPLETED: "Completed"
    };

    return statusLabels[status] || status || "-";
}
/* =========================================
   ELEMENTS
========================================= */

const taskList = document.getElementById("task-list");
const refreshButton = document.getElementById("refresh-button");

const taskModal = document.getElementById("task-modal");
const closeModal = document.getElementById("close-modal");
const closeModalButton = document.getElementById("close-modal-button");

let allTasks = [];

/* =========================================
   LOAD EMPLOYEE TASKS
========================================= */

async function loadTasks() {
    if (!taskList) {
        return;
    }

    taskList.innerHTML = `
        <p class="loading">
            Loading tasks...
        </p>
    `;

    try {
        const response = await fetch(
    `${API_URL}/tasks`,
    {
        headers: authHeaders()
    }
);

        const data = await response.json();

        console.log("Tasks returned by API:", data);

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to load tasks"
            );
        }

        allTasks = data.tasks || [];

        updateStatistics(allTasks);
        displayTasks(allTasks);

    } catch (error) {
        console.error(
            "Failed to load tasks:",
            error
        );

        taskList.innerHTML = `
            <div class="error">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

/* =========================================
   LOAD MANAGER TASKS
========================================= */

async function loadManagerTasks() {
    const managerTaskList =
        document.getElementById("manager-task-list");

    if (!managerTaskList) {
        return;
    }

    managerTaskList.innerHTML = `
        <p class="loading">
            Loading manager tasks...
        </p>
    `;

    try {
        const response = await fetch(
    `${API_URL}/tasks`,
    {
        headers: authHeaders()
    }
);

        const data = await response.json();

        console.log(
            "Manager tasks returned by API:",
            data
        );

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to load manager tasks"
            );
        }

        const managerTasks = data.tasks || [];

        displayManagerTasks(managerTasks);

    } catch (error) {
        console.error(
            "Failed to load manager tasks:",
            error
        );

        managerTaskList.innerHTML = `
            <div class="error">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

/* =========================================
   UPDATE STATISTICS
========================================= */

function updateStatistics(tasks) {
    const totalTasks =
        document.getElementById("total-tasks");

    const progressTasks =
        document.getElementById("progress-tasks");

    const completedTasks =
        document.getElementById("completed-tasks");

    const pendingTasks =
        document.getElementById("pending-tasks");

    if (totalTasks) {
        totalTasks.textContent = tasks.length;
    }

    if (progressTasks) {
        progressTasks.textContent =
            tasks.filter(
                task => task.status === "IN_PROGRESS"
            ).length;
    }

    if (completedTasks) {
        completedTasks.textContent =
            tasks.filter(
                task => task.status === "COMPLETED"
            ).length;
    }

    if (pendingTasks) {
        pendingTasks.textContent =
            tasks.filter(
                task => task.status === "PENDING_APPROVAL"
            ).length;
    }
}

/* =========================================
   DISPLAY EMPLOYEE TASKS
========================================= */

function displayTasks(tasks) {
    if (!taskList) {
        return;
    }

    if (!tasks || tasks.length === 0) {
        taskList.innerHTML = `
            <p class="loading">
                No tasks found.
            </p>
        `;
        return;
    }

    taskList.innerHTML = "";

    tasks.forEach(function (task) {
        const taskCard =
            document.createElement("div");

        taskCard.className = "task-card";

        taskCard.innerHTML = `
            <h3>
                ${escapeHtml(
                    task.title || "Untitled Task"
                )}
            </h3>

            <p class="task-description">
                ${escapeHtml(
                    task.description ||
                    "No description provided."
                )}
            </p>

            <div class="task-details">

                <span>
                    Status:
                    <strong class="status">
                        ${escapeHtml(
    formatTaskStatus(task.status)
)}
                    </strong>
                </span>

                <span>
                    Priority:
                    <strong class="priority">
                        ${escapeHtml(
                            task.priority || "-"
                        )}
                    </strong>
                </span>

            </div>

            <div class="task-actions">

                <button
                    class="view-button"
                    type="button">
                    View Task
                </button>

                ${
                    task.status === "MANAGED"
                        ? `
                            <button
                                class="start-button"
                                type="button">
                                Start Task
                            </button>
                        `
                        : ""
                }

                ${
                    task.status === "IN_PROGRESS"
                        ? `
                            <button
                                class="complete-button"
                                type="button">
                                Complete Task
                            </button>
                        `
                        : ""
                }

            </div>
        `;

        /* VIEW TASK */

        const viewButton =
            taskCard.querySelector(".view-button");

        if (viewButton) {
            viewButton.addEventListener(
                "click",
                function () {
                    console.log(
                        "View Task clicked:",
                        task
                    );

                    openTaskModal(task);
                }
            );
        }

        /* START TASK */

        const startButton =
            taskCard.querySelector(".start-button");

        if (startButton) {
            startButton.addEventListener(
                "click",
                function () {
                    startTask(task.id);
                }
            );
        }

        /* COMPLETE TASK */

        const completeButton =
            taskCard.querySelector(
                ".complete-button"
            );

        if (completeButton) {
            completeButton.addEventListener(
                "click",
                function () {
                    completeTask(task.id);
                }
            );
        }

        taskList.appendChild(taskCard);
    });
}

/* =========================================
   DISPLAY MANAGER TASKS
========================================= */

function displayManagerTasks(tasks) {
    const managerTaskList =
        document.getElementById(
            "manager-task-list"
        );

    if (!managerTaskList) {
        return;
    }

    if (!tasks || tasks.length === 0) {
        managerTaskList.innerHTML = `
            <p class="loading">
                No manager tasks found.
            </p>
        `;
        return;
    }

    managerTaskList.innerHTML = "";

    tasks.forEach(function (task) {
        const taskCard =
            document.createElement("div");

        taskCard.className = "task-card";

        taskCard.innerHTML = `
            <h3>
                ${escapeHtml(
                    task.title || "Untitled Task"
                )}
            </h3>

            <p class="task-description">
                ${escapeHtml(
                    task.description ||
                    "No description provided."
                )}
            </p>

            <div class="task-details">

                <span>
                    Status:
                    <strong class="status">
                        ${escapeHtml(
                            formatTaskStatus(task.status)
                       )}
                    </strong>
                </span>

                <span>
                    Priority:
                    <strong class="priority">
                        ${escapeHtml(
                            task.priority || "-"
                        )}
                    </strong>
                </span>

                <span>
                    Assigned To:
                    <strong>
                        User ${
                            task.assigned_to || "-"
                        }
                    </strong>
                </span>

            </div>

            <div class="task-actions">

                <button
                    class="view-manager-button"
                    type="button">
                    View Task
                </button>

                ${
                    task.status === "PENDING"
                        ? `
                            <button
                                class="manage-button"
                                type="button">
                                Manage Task
                            </button>
                        `
                        : ""
                }

                ${
                    task.status === "PENDING_APPROVAL"
                        ? `
                            <button
                                class="approve-button"
                                type="button">
                                Approve
                            </button>

                            <button
                                class="reject-button"
                                type="button">
                                Reject
                            </button>
                        `
                        : ""
                }

                ${
                    task.status === "REJECTED"
                        ? `
                            <button
                                class="rework-button"
                                type="button">
                                Send for Rework
                            </button>
                        `
                        : ""
                }

            </div>
        `;

        /* VIEW MANAGER TASK */

        const viewButton =
            taskCard.querySelector(
                ".view-manager-button"
            );

        if (viewButton) {
            viewButton.addEventListener(
                "click",
                function () {
                    openTaskModal(task);
                }
            );
        }

        /* MANAGE TASK */

        const manageButton = taskCard.querySelector(".manage-button");

        if (manageButton) {
            manageButton.addEventListener("click", function () {
                manageTask(task.id);
            });
        }

        /* APPROVE TASK */

        const approveButton =
            taskCard.querySelector(
                ".approve-button"
            );

        if (approveButton) {
            approveButton.addEventListener(
                "click",
                function () {
                    approveTask(task.id);
                }
            );
        }
        /* REJECT TASK */

const rejectButton =
    taskCard.querySelector(
        ".reject-button"
    );

if (rejectButton) {
    rejectButton.addEventListener(
        "click",
        function () {
            rejectTask(task.id);
        }
    );
}
/* REWORK TASK */

const reworkButton =
    taskCard.querySelector(
        ".rework-button"
    );

if (reworkButton) {
    reworkButton.addEventListener(
        "click",
        function () {
            reworkTask(task.id);
        }
    );
}

        managerTaskList.appendChild(taskCard);
    });
}

/* =========================================
   OPEN TASK MODAL
========================================= */

function openTaskModal(task) {
    console.log(
        "Opening task modal:",
        task
    );

    document.getElementById(
        "modal-title"
    ).textContent =
        task.title || "No title";

    document.getElementById(
        "modal-description"
    ).textContent =
        task.description ||
        "No description provided";

    document.getElementById(
        "modal-status"
    ).textContent =
        task.status || "-";

    document.getElementById(
        "modal-priority"
    ).textContent =
        task.priority || "-";

    document.getElementById(
        "modal-id"
    ).textContent =
        task.id !== undefined &&
        task.id !== null
            ? task.id
            : "-";

    document.getElementById(
        "modal-assigned"
    ).textContent =
        task.assigned_to !== undefined &&
        task.assigned_to !== null
            ? `User ${task.assigned_to}`
            : "Not assigned";

    document.getElementById(
        "modal-created-by"
    ).textContent =
        task.created_by !== undefined &&
        task.created_by !== null
            ? `User ${task.created_by}`
            : "Unknown";

    document.getElementById(
        "modal-due-date"
    ).textContent =
        task.due_date
            ? formatDate(task.due_date)
            : "No due date";

    document.getElementById(
        "modal-created-at"
    ).textContent =
        task.created_at
            ? formatDate(task.created_at)
            : "-";

    document.getElementById(
        "modal-updated-at"
    ).textContent =
        task.updated_at
            ? formatDate(task.updated_at)
            : "-";

    if (taskModal) {
        taskModal.classList.add("show");
    }
}

/* =========================================
   FORMAT DATE
========================================= */

function formatDate(dateValue) {
    if (!dateValue) {
        return "-";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return dateValue;
    }

    return date.toLocaleString();
}

/* =========================================
   CLOSE TASK MODAL
========================================= */

function closeTaskModal() {
    if (taskModal) {
        taskModal.classList.remove("show");
    }
}

if (closeModal) {
    closeModal.addEventListener(
        "click",
        closeTaskModal
    );
}

if (closeModalButton) {
    closeModalButton.addEventListener(
        "click",
        closeTaskModal
    );
}

/* CLOSE MODAL WHEN CLICKING OUTSIDE */

if (taskModal) {
    taskModal.addEventListener(
        "click",
        function (event) {
            if (event.target === taskModal) {
                closeTaskModal();
            }
        }
    );
}

/* =========================================
   START TASK
========================================= */

async function startTask(taskId) {
    try {
       const response = await fetch(
    `${API_URL}/tasks/${taskId}/start`,
    {
        method: "PUT",
        headers: authHeaders()
    }
);

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                "Failed to start task"
            );
        }

        await loadTasks();

    } catch (error) {
        console.error(
            "Start task error:",
            error
        );

        alert(error.message);
    }
}

/* =========================================
   COMPLETE TASK
========================================= */

async function completeTask(taskId) {
    try {
        const response = await fetch(
    `${API_URL}/tasks/${taskId}/complete`,
    {
        method: "PUT",
        headers: authHeaders()
    }
);

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                "Failed to complete task"
            );
        }

        await loadTasks();

    } catch (error) {
        console.error(
            "Complete task error:",
            error
        );

        alert(error.message);
    }
}


/* =========================================
   MANAGE TASK
========================================= */

async function manageTask(taskId) {
    try {
        const response = await fetch(
    `${API_URL}/tasks/${taskId}/manage`,
    {
        method: "PUT",
        headers: authHeaders()
    }
);

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to manage task"
            );
        }

        alert("Task managed successfully.");

        await loadManagerTasks();

    } catch (error) {
        console.error("Manage task error:", error);
        alert(error.message);
    }
}

/* =========================================
   APPROVE TASK
========================================= */

async function approveTask(taskId) {
    try {
        const response = await fetch(
    `${API_URL}/tasks/${taskId}/approve`,
    {
        method: "PUT",
        headers: authHeaders()
    }
);
        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                "Failed to approve task"
            );
        }

        alert(
            "Task approved successfully."
        );

        await loadManagerTasks();

    } catch (error) {
        console.error(
            "Approve task error:",
            error
        );

        alert(error.message);
    }
}

/* =========================================
   REJECT TASK
========================================= */

async function rejectTask(taskId) {
    const comment = prompt(
        "Please enter a reason for rejecting this task:"
    );

    if (!comment) {
        return;
    }

    try {
        const response = await fetch(
    `${API_URL}/tasks/${taskId}/reject`,
    {
        method: "PUT",
        headers: {
            ...authHeaders(),
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            comment: comment
        })
    }
);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to reject task"
            );
        }

        alert("Task rejected successfully.");

        await loadManagerTasks();

    } catch (error) {
        console.error("Reject task error:", error);
        alert(error.message);
    }
}



/* =========================================
   REWORK TASK
========================================= */

async function reworkTask(taskId) {
    try {
        const response = await fetch(
    `${API_URL}/tasks/${taskId}/rework`,
    {
        method: "PUT",
        headers: authHeaders()
    }
);

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to send task for rework"
            );
        }

        alert("Task sent for rework successfully.");

        await loadManagerTasks();

    } catch (error) {
        console.error("Rework task error:", error);
        alert(error.message);
    }
}

/* =========================================
   REFRESH BUTTON
========================================= */

if (refreshButton) {
    refreshButton.addEventListener(
        "click",
        loadTasks
    );
}

/* =========================================
   SIDEBAR LINKS
========================================= */

const dashboardLink =
    document.getElementById(
        "dashboard-link"
    );

const tasksLink =
    document.getElementById(
        "tasks-link"
    );

const completedLink =
    document.getElementById(
        "completed-link"
    );

const managerLink =
    document.getElementById(
        "manager-link"
    );

/* =========================================
   NAVIGATION
========================================= */

function activateNavigation(
    activeLink
) {
    document
        .querySelectorAll(".nav-item")
        .forEach(function (link) {
            link.classList.remove(
                "active"
            );
        });

    if (activeLink) {
        activeLink.classList.add(
            "active"
        );
    }
}

/* =========================================
   DASHBOARD
========================================= */

if (dashboardLink) {
    dashboardLink.addEventListener(
        "click",
        function (event) {
            event.preventDefault();

            activateNavigation(
                dashboardLink
            );

            document
                .getElementById("dashboard")
                ?.scrollIntoView({
                    behavior: "smooth"
                });
        }
    );
}

/* =========================================
   MY TASKS
========================================= */

if (tasksLink) {
    tasksLink.addEventListener(
        "click",
        function (event) {
            event.preventDefault();

            activateNavigation(
                tasksLink
            );

            displayTasks(
                allTasks
            );

            document
                .getElementById("tasks")
                ?.scrollIntoView({
                    behavior: "smooth"
                });
        }
    );
}

/* =========================================
   COMPLETED
========================================= */

if (completedLink) {
    completedLink.addEventListener(
        "click",
        function (event) {
            event.preventDefault();

            activateNavigation(
                completedLink
            );

            const completedTasks =
                allTasks.filter(
                    function (task) {
                        return (
                            task.status ===
                            "COMPLETED"
                        );
                    }
                );

            displayTasks(
                completedTasks
            );

            document
                .getElementById("tasks")
                ?.scrollIntoView({
                    behavior: "smooth"
                });
        }
    );
}

/* =========================================
   MANAGER
========================================= */

if (managerLink) {
    managerLink.addEventListener(
        "click",
        function (event) {
            event.preventDefault();

            activateNavigation(
                managerLink
            );

            loadManagerTasks();

            document
                .getElementById("manager")
                ?.scrollIntoView({
                    behavior: "smooth"
                });
        }
    );
}

/* =========================================
   ESCAPE HTML
========================================= */

function escapeHtml(value) {
    if (
        value === undefined ||
        value === null
    ) {
        return "";
    }

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}

/* =========================================
   INITIAL LOAD
========================================= */

loadTasks();



