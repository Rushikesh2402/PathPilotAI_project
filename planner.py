
from datetime import date
from ortools.sat.python import cp_model

TASK_LIBRARY = {
    "coding": [
        ("Learn programming fundamentals", 2, 5),
        ("Practice coding problems", 2, 5),
        ("Solve array and string problems", 2, 4),
        ("Review mistakes and solutions", 1, 3)
    ],
    "placement": [
        ("Practice quantitative aptitude", 1, 4),
        ("Practice data structures and algorithms", 2, 5),
        ("Prepare interview questions", 1, 3),
        ("Take a mock interview", 1, 4)
    ],
    "exam": [
        ("Review important concepts", 2, 5),
        ("Solve practice questions", 2, 5),
        ("Revise difficult topics", 1, 4),
        ("Attempt a mock test", 2, 4)
    ],
    "skill": [
        ("Study core concepts", 1, 4),
        ("Complete a practical exercise", 2, 5),
        ("Build a mini project", 2, 4),
        ("Review and improve your work", 1, 3)
    ],
    "dsa": [
        ("Study arrays and strings", 2, 5),
        ("Practice linked lists and stacks", 2, 4),
        ("Solve sorting and searching problems", 2, 5),
        ("Practice trees and graphs", 2, 4)
    ]
}

def create_plan(goal_data):
    goal = goal_data["goal"]
    deadline = date.fromisoformat(goal_data["deadline"])
    daily_hours = float(goal_data["daily_hours"])
    days = (deadline - date.today()).days + 1

    if days <= 0:
        raise ValueError("Deadline must be in the future.")

    if not 0 < daily_hours <= 24:
        raise ValueError("Daily hours must be between 0 and 24.")

    text = goal.lower()
    tasks = []
    seen = set()

    for keyword, items in TASK_LIBRARY.items():
        if keyword in text or keyword in goal_data["keywords"]:
            for title, hours, priority in items:
                if title not in seen:
                    tasks.append({
                        "title": title,
                        "hours": hours,
                        "priority": priority
                    })
                    seen.add(title)

    if not tasks:
        tasks = [
            {"title": f"Study {goal}", "hours": 1, "priority": 5},
            {"title": "Practice what you learned", "hours": 1, "priority": 4},
            {"title": "Review progress", "hours": 1, "priority": 3}
        ]

    model = cp_model.CpModel()
    selected = [
        model.new_bool_var(f"task_{i}")
        for i in range(len(tasks))
    ]

    model.add(
        sum(tasks[i]["hours"] * selected[i]
            for i in range(len(tasks)))
        <= int(daily_hours * days)
    )

    model.maximize(
        sum(tasks[i]["priority"] * selected[i]
            for i in range(len(tasks)))
    )

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError("No feasible schedule found.")

    chosen = [
        {**task, "status": "Pending"}
        for i, task in enumerate(tasks)
        if solver.value(selected[i])
    ]
    chosen.sort(key=lambda task: task["priority"], reverse=True)

    return {
        "goal": goal,
        "deadline": deadline.isoformat(),
        "available_days": days,
        "tasks": chosen
    }

def replan_tasks(tasks, daily_hours, days_remaining):
    pending = [
        task for task in tasks
        if task["status"] != "Completed"
    ]

    if days_remaining <= 0:
        raise ValueError("No time remains before the deadline.")

    model = cp_model.CpModel()
    selected = [
        model.new_bool_var(f"replan_{i}")
        for i in range(len(pending))
    ]

    model.add(
        sum(pending[i]["hours"] * selected[i]
            for i in range(len(pending)))
        <= int(daily_hours * days_remaining)
    )

    model.maximize(
        sum(pending[i]["priority"] * selected[i]
            for i in range(len(pending)))
    )

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError("No feasible revised plan found.")

    return [
        {
            **task,
            "status": "Pending",
            "explanation": (
                "Rescheduled based on remaining time and task priority."
            )
        }
        for i, task in enumerate(pending)
        if solver.value(selected[i])
    ]
