# NIAI Attendance — User Flow

## 1. Teacher account

1. Open the web app.
2. Choose **Sign up** on the animated login card.
3. Enter name, email and an 8+ character password.
4. The account is created as a `teacher` and the teacher is logged in automatically.
5. Existing teachers use **Login** with their own email/password.

A seeded demo account remains available after running `python -m app.seed`:
- `teacher@example.com`
- `Teacher123!`

## 2. Create/edit a class session

Open **Class sessions** after login.

The teacher can enter:
- Class/session title
- Course
- Date
- Start time
- End time

For example: `AI Class` / `Artificial Intelligence` / `Monday` / `7:00 PM` / `10:00 PM`.

Existing sessions have **Edit** and **Delete** actions. Editing the schedule resets its reminder status so a changed future session can send its reminder again.

## 3. Email reminder

Set these values in `backend/.env`:

```env
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=yourgmail@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM=yourgmail@gmail.com
NOTIFICATION_EMAIL=sir@example.com
TIMEZONE=Asia/Karachi
```

The scheduler checks every 15 seconds. When a session reaches its configured start time, an email is sent to `NOTIFICATION_EMAIL` (or to the logged-in teacher if that setting is blank).

**Friday, Saturday and Sunday are skipped automatically.**

## 4. Attendance

Go to **Scan register**, upload JPG/PNG/WEBP/PDF, and wait for processing.

The result screen provides:
- Present
- Absent
- Leave
- Total
- Confidence
- CSV download
- Browser print

The current parser is a generic OCR baseline. A real handwritten monthly register should be calibrated to its exact grid/cell layout before treating its totals as production-accurate.

## 5. Local run

Backend terminal:

```powershell
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8001
```

Frontend terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.
