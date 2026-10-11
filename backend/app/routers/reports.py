import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import AttendanceRun, User
from ..security import current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(current_user)):
    q = db.query(AttendanceRun)
    if user.role != "admin":
        q = q.filter(AttendanceRun.teacher_id == user.id)
    runs = q.order_by(AttendanceRun.created_at.desc()).limit(100).all()
    students = {}
    for run in runs:
        for row in json.loads(run.result_json).get("rows", []):
            name = row.get("student", "").strip()
            if not name:
                continue
            s = students.setdefault(name, {"student": name, "present": 0, "absent": 0, "leave": 0})
            s["present"] += row.get("present", 0)
            s["absent"] += row.get("absent", 0)
            s["leave"] += row.get("leave", 0)
    for s in students.values():
        total = s["present"] + s["absent"] + s["leave"]
        s["attendance_pct"] = round(s["present"] / total * 100, 1) if total else 0
    return {"runs": len(runs), "students": sorted(students.values(), key=lambda x: x["attendance_pct"])}
