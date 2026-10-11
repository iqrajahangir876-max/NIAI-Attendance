from pathlib import Path
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password

Path("./data").mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

users = [
    ("Admin", "admin@example.com", "Admin123!", "admin"),
    ("Demo Teacher", "teacher@example.com", "Teacher123!", "teacher"),
]
for name, email, password, role in users:
    if not db.query(User).filter(User.email == email).first():
        db.add(User(name=name, email=email, password_hash=hash_password(password), role=role))
db.commit()
db.close()
print("Seed complete.")
