from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class SessionCreate(BaseModel):
    title: str
    course: str = ""
    starts_at: datetime
    duration_minutes: int = Field(default=180, ge=5, le=720)
    # 0 = send exactly when the attendance/class time starts.
    reminder_minutes: int = Field(default=0, ge=0, le=10080)

class SessionUpdate(BaseModel):
    title: str
    course: str = ""
    starts_at: datetime
    duration_minutes: int = Field(default=180, ge=5, le=720)
    reminder_minutes: int = Field(default=0, ge=0, le=10080)

class SessionOut(SessionCreate):
    id: int
    teacher_id: int
    reminder_sent: bool
    class Config:
        from_attributes = True
