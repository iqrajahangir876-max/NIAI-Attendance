import smtplib
from email.message import EmailMessage
from . import __name__  # keeps package import explicit
from ..config import get_settings

def send_email(to_email: str, subject: str, body: str):
    settings = get_settings()
    if not settings.smtp_enabled:
        return False
    msg = EmailMessage()
    msg["From"] = settings.smtp_from or settings.smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)
    return True
