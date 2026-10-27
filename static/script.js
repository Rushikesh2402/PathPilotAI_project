
const form = document.getElementById("goalForm");
const result = document.getElementById("result");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    result.textContent = "Generating your roadmap...";

    try {
        const response = await fetch("/generate", {
            method: "POST",
            body: new FormData(form)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(getErrorMessage(data));
        }

        displayPlan(data.plan, data.plan_id);
    } catch (error) {
        result.textContent = error.message || "Unable to generate roadmap.";
    }
});

function getErrorMessage(data) {
    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (data.detail) {
        return JSON.stringify(data.detail);
    }

    return "Request failed. Please try again.";
}

function displayPlan(plan, planId) {
    result.replaceChildren();

    const summary = document.createElement("p");
    summary.textContent =
        `Goal: ${plan.goal} | Deadline: ${plan.deadline}`;
    result.appendChild(summary);

    const heading = document.createElement("h3");
    heading.textContent = "Prioritized Tasks";
    result.appendChild(heading);

    if (!plan.tasks || plan.tasks.length === 0) {
        const message = document.createElement("p");
        message.textContent = "No tasks fit the current time constraints.";
        result.appendChild(message);
        return;
    }

    const progress = document.createElement("p");
    result.appendChild(progress);

    function updateProgress() {
        const completed = plan.tasks.filter(
            task => task.status === "Completed"
        ).length;

        progress.textContent =
            `Progress: ${completed}/${plan.tasks.length} tasks completed`;
    }

    updateProgress();

    plan.tasks.forEach((task, index) => {
        const card = document.createElement("div");
        card.className = "task";

        const title = document.createElement("strong");
        title.textContent = `${index + 1}. ${task.title}`;

        const details = document.createElement("p");
        details.textContent =
            `${task.hours} hour(s) | Priority: ${task.priority}`;

        const status = document.createElement("p");
        status.textContent = `Status: ${task.status || "Pending"}`;

        const controls = document.createElement("div");
        controls.className = "task-controls";

        ["Completed", "Missed", "Pending"].forEach(value => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "status-button";
            button.textContent = value;

            button.addEventListener("click", async () => {
                const buttons = controls.querySelectorAll("button");
                buttons.forEach(item => item.disabled = true);

                try {
                    if (!task.id) {
                        throw new Error(
                            "This task has no database ID. Please generate a new roadmap."
                        );
                    }

                    const body = new FormData();
                    body.append("status", value);

                    const response = await fetch(
                        `/task/${task.id}/status`,
                        {
                            method: "POST",
                            body: body
                        }
                    );

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(getErrorMessage(data));
                    }

                    task.status = data.status || value;
                    status.textContent = `Status: ${task.status}`;
                    updateProgress();
                } catch (error) {
                    alert(error.message || "Unable to update task status.");
                } finally {
                    buttons.forEach(item => item.disabled = false);
                }
            });

            controls.appendChild(button);
        });

        card.append(title, details, status, controls);
        result.appendChild(card);
    });
}
