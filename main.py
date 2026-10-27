
from datetime import date
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from goal_parser import parse_goal
from planner import create_plan
from database import init_db, save_plan, get_plan, update_task_status

app = FastAPI(title="PathPilot AI")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"today": date.today().isoformat()}
    )

@app.post("/generate")
def generate_plan(
    goal: str = Form(...),
    deadline: str = Form(...),
    daily_hours: float = Form(...)
):
    if not goal.strip():
        raise HTTPException(status_code=400, detail="Enter a goal.")

    try:
        goal_data = parse_goal(goal, deadline, daily_hours)
        plan = create_plan(goal_data)
        plan_id = save_plan(goal_data, plan)
        return {
            "plan_id": plan_id,
            "goal_data": goal_data,
            "plan": plan
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.get("/plan/{plan_id}")
def read_plan(plan_id: int):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")
    return plan

@app.post("/task/{task_id}/status")
def change_task_status(task_id: int, status: str = Form(...)):
    if status not in ("Pending", "Completed", "Missed"):
        raise HTTPException(status_code=400, detail="Invalid task status.")

    updated = update_task_status(task_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found.")

    return {"message": "Task status updated.", "status": status}
