
import sqlite3
import json

DB_NAME = "pathpilot.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                deadline TEXT NOT NULL,
                daily_hours REAL NOT NULL,
                plan_json TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                hours REAL NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                explanation TEXT DEFAULT '',
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)


def save_plan(goal_data, plan):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            """
            INSERT INTO plans (goal, deadline, daily_hours, plan_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                goal_data["goal"],
                goal_data["deadline"],
                float(goal_data["daily_hours"]),
                json.dumps(plan)
            )
        )

        plan_id = cursor.lastrowid

        for task in plan.get("tasks", []):
            task_cursor = conn.execute(
                """
                INSERT INTO tasks
                (plan_id, title, hours, priority, status, explanation)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    task["title"],
                    float(task["hours"]),
                    int(task["priority"]),
                    task.get("status", "Pending"),
                    task.get("explanation", "Prioritized by the planning system.")
                )
            )

            task["id"] = task_cursor.lastrowid
            task["status"] = task.get("status", "Pending")

        return plan_id


def get_plan(plan_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        plan_row = conn.execute(
            "SELECT * FROM plans WHERE id = ?",
            (plan_id,)
        ).fetchone()

        if plan_row is None:
            return None

        task_rows = conn.execute(
            """
            SELECT id, title, hours, priority, status, explanation
            FROM tasks
            WHERE plan_id = ?
            ORDER BY priority DESC, id ASC
            """,
            (plan_id,)
        ).fetchall()

        saved_plan = json.loads(plan_row["plan_json"])

        saved_plan["plan_id"] = plan_row["id"]
        saved_plan["goal"] = plan_row["goal"]
        saved_plan["deadline"] = plan_row["deadline"]
        saved_plan["daily_hours"] = plan_row["daily_hours"]
        saved_plan["tasks"] = [dict(task) for task in task_rows]

        return saved_plan


def update_task_status(task_id, status):
    allowed_statuses = ("Pending", "Completed", "Missed")

    if status not in allowed_statuses:
        return False

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )

        return cursor.rowcount > 0
