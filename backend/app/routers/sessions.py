from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Session as SessionModel, User
from ..schemas import SessionCreate, SessionUpdate, SessionOut
from ..security import current_user

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.get("", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_db), user: User = Depends(current_user)):
    q = db.query(SessionModel).order_by(SessionModel.starts_at.asc())
    if user.role != "admin":
        q = q.filter(SessionModel.teacher_id == user.id)
    return q.limit(100).all()

@router.post("", response_model=SessionOut)
def create_session(payload: SessionCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = SessionModel(teacher_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.put("/{session_id}", response_model=SessionOut)
def update_session(session_id: int, payload: SessionUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.get(SessionModel, session_id)
    if not row or (user.role != "admin" and row.teacher_id != user.id):
        raise HTTPException(404, "Session not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    # Changing the schedule should allow the reminder to be sent again.
    row.reminder_sent = False
    db.commit()
    db.refresh(row)
    return row

@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.get(SessionModel, session_id)
    if not row or (user.role != "admin" and row.teacher_id != user.id):
        raise HTTPException(404, "Session not found")
    db.delete(row)
    db.commit()
    return {"ok": True}
