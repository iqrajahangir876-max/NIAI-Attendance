from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from .config import get_settings
from .database import Base, engine, SessionLocal
from .models import Session as SessionModel, User
from .services.mailer import send_email
from .routers import auth, attendance, sessions, reports, manual

settings = get_settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path("./data").mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.1.0")
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(sessions.router)
app.include_router(reports.router)
app.include_router(manual.router)

scheduler = BackgroundScheduler()

# NIAI stores session datetimes as naive local datetimes. Treat them as Pakistan time.
PKT = ZoneInfo(settings.timezone)


def send_due_reminders():
    """Send class-start emails. Friday/Saturday/Sunday are intentionally skipped."""
    if not settings.smtp_enabled:
        return

    db = SessionLocal()
    try:
        now = datetime.now(PKT).replace(tzinfo=None)
        # Monday=0 ... Friday=4, Saturday=5, Sunday=6.
        if now.weekday() >= 4:
            return

        # A 3-minute safety window prevents missing a reminder if the scheduler
        # wakes a little late. reminder_minutes=0 means "at class start".
        candidates = (
            db.query(SessionModel)
            .filter(SessionModel.reminder_sent == False)
            .all()
        )

        for session in candidates:
            due_at = session.starts_at - timedelta(minutes=session.reminder_minutes or 0)
            if not (now - timedelta(minutes=3) <= due_at <= now + timedelta(minutes=3)):
                continue
            # Also skip a session whose own date falls on Fri/Sat/Sun.
            if session.starts_at.weekday() >= 4:
                session.reminder_sent = True
                continue

            teacher = db.get(User, session.teacher_id)
            if not teacher:
                continue

            recipient = settings.notification_email.strip() or teacher.email
            end_at = session.starts_at + timedelta(minutes=session.duration_minutes)
            subject = f"NIAI Attendance — {session.title} has started"
            body = (
                f"Assalam-o-Alaikum,\n\n"
                f"NIAI Attendance reminder: your session has started.\n\n"
                f"Class: {session.title}\n"
                f"Course: {session.course or 'N/A'}\n"
                f"Date: {session.starts_at:%A, %d %B %Y}\n"
                f"Time: {session.starts_at:%I:%M %p} - {end_at:%I:%M %p}\n\n"
                f"Please open NIAI Attendance to take/process the attendance register.\n\n"
                f"NIAI Attendance"
            )

            try:
                sent = send_email(recipient, subject, body)
                if sent:
                    session.reminder_sent = True
            except Exception as exc:
                # Keep the scheduler alive; retry on the next tick.
                print(f"Email reminder failed for session {session.id}: {exc}")

        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            send_due_reminders,
            "interval",
            seconds=15,
            id="session-reminders",
            replace_existing=True,
        )
        scheduler.start()


@app.on_event("shutdown")
def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)


@app.get("/health")
def health():
    return {"ok": True, "service": settings.app_name, "timezone": settings.timezone}
