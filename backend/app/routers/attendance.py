import json
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import get_db
from ..models import AttendanceRun, User
from ..security import current_user
from ..services.file_pipeline import process_file
from ..services.csv_service import rows_to_csv
from fastapi.responses import Response

router = APIRouter(prefix="/api/attendance", tags=["attendance"])

@router.post("/process")
async def process_attendance(
    file: UploadFile = File(...),
    session_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".pdf"}:
        raise HTTPException(400, "Upload JPG, PNG, WEBP or PDF")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, "File too large")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    work_name = f"{uuid.uuid4().hex}{suffix}"
    saved = upload_dir / work_name
    saved.write_bytes(data)

    try:
        result = process_file(str(saved), str(upload_dir))
    except Exception as exc:
        raise HTTPException(422, f"Could not process register: {exc}")

    run = AttendanceRun(
        teacher_id=user.id,
        session_id=session_id,
        original_filename=file.filename or work_name,
        confidence=result["ocr_confidence"],
        raw_ocr=result["raw_text"],
        result_json=json.dumps(result),
        status="review" if result["needs_review"] else "completed",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return {"run_id": run.id, **result}

@router.get("/runs")
def list_runs(db: Session = Depends(get_db), user: User = Depends(current_user)):
    q = db.query(AttendanceRun).order_by(AttendanceRun.created_at.desc())
    if user.role != "admin":
        q = q.filter(AttendanceRun.teacher_id == user.id)
    return [
        {
            "id": r.id, "filename": r.original_filename,
            "status": r.status, "confidence": r.confidence,
            "created_at": r.created_at.isoformat()
        } for r in q.limit(100).all()
    ]

@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    r = db.get(AttendanceRun, run_id)
    if not r or (user.role != "admin" and r.teacher_id != user.id):
        raise HTTPException(404, "Run not found")
    return {"id": r.id, **json.loads(r.result_json)}

@router.get("/runs/{run_id}/csv")
def csv_report(run_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    r = db.get(AttendanceRun, run_id)
    if not r or (user.role != "admin" and r.teacher_id != user.id):
        raise HTTPException(404, "Run not found")
    payload = json.loads(r.result_json)
    csv_text = rows_to_csv(payload.get("rows", []))
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="niai-attendance-{run_id}.csv"'}
    )
