from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Student, ManualAttendance, Session as SessionModel
from ..security import current_user

router = APIRouter(prefix="/api/manual", tags=["manual attendance"])

DEFAULT_STUDENTS = [
    "Abdul Rehman", "Abdul Wahab", "Abdul Ahad", "Adeel Bin Asghar", "Ahtasham Ali",
    "Ali Maaz", "Ali Subbyan", "Amna Nawaz", "Aneeq Ahmad", "Arif Ullah Khan",
    "Asad Ali", "Asad Ullah", "Asim Javed", "Aziz Ahmad", "Haseeb Ahmad",
    "Huma Aslam", "Hussain Ali", "Husnain Dawood", "Iqra Jahangir", "Khawaja Subhan",
    "Lumia Noman", "M. Shehrozad", "Majid Yaseen", "Minhaj Aftab", "Muazam Ali",
    "Muhammad Abdullah (553)", "Muhammad Abdullah (463)", "Muhammad Ars", "Nadir Ahmad",
    "Rizwan Riaz", "Syed M. Qasim Jamil", "Tahir Raza Shah", "Taha"
]

class MarkIn(BaseModel):
    session_id: int
    student_id: int
    status: str


def ensure_roster(db: Session):
    if db.query(Student).count() == 0:
        db.add_all([Student(name=name) for name in DEFAULT_STUDENTS])
        db.commit()
    return db.query(Student).filter(Student.active == True).order_by(Student.id).all()

@router.get("/students")
def students(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return [{"id": s.id, "name": s.name} for s in ensure_roster(db)]

@router.get("/session/{session_id}")
def session_attendance(session_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    session = db.get(SessionModel, session_id)
    if not session or (user.role != "admin" and session.teacher_id != user.id):
        raise HTTPException(404, "Session not found")
    roster = ensure_roster(db)
    existing = {x.student_id: x.status for x in db.query(ManualAttendance).filter(ManualAttendance.session_id == session_id, ManualAttendance.teacher_id == user.id).all()}
    return [{"id": s.id, "name": s.name, "status": existing.get(s.id, "PRESENT")} for s in roster]

@router.post("/mark")
def mark(payload: MarkIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    session = db.get(SessionModel, payload.session_id)
    student = db.get(Student, payload.student_id)
    status = payload.status.upper()
    if not session or not student or (user.role != "admin" and session.teacher_id != user.id):
        raise HTTPException(404, "Session or student not found")
    if status not in {"PRESENT", "ABSENT", "LEAVE"}:
        raise HTTPException(400, "Status must be PRESENT, ABSENT or LEAVE")
    row = db.query(ManualAttendance).filter_by(teacher_id=user.id, session_id=session.id, student_id=student.id).first()
    if not row:
        row = ManualAttendance(teacher_id=user.id, session_id=session.id, student_id=student.id, status=status)
        db.add(row)
    else:
        row.status = status
    db.commit()
    return {"ok": True, "student_id": student.id, "status": status}
