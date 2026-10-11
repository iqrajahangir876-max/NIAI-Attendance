# NIAI Attendance — Session Email Setup

## What changed

- Teacher can create a class with a start and end time from the **Class sessions** screen.
- Example: **7:00 PM – 10:00 PM**.
- The default email reminder is sent at the session start time.
- Friday, Saturday and Sunday reminders are skipped automatically.
- Sessions can be edited later; editing resets the reminder so the new time can be used.
- The recipient can be set globally with `NOTIFICATION_EMAIL`.
- If `NOTIFICATION_EMAIL` is empty, the logged-in teacher's account email is used.
- Schedule times use `Asia/Karachi` by default.

## Files involved

### Backend

- `backend/app/config.py`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/routers/sessions.py`
- `backend/.env.example`

### Frontend

- `frontend/src/App.tsx`
- `frontend/src/api.ts`
- `frontend/src/styles.css`
- `frontend/.env.example`

## Gmail SMTP example

In `backend/.env`:

```env
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=youraccount@gmail.com
SMTP_PASSWORD=YOUR_GMAIL_APP_PASSWORD
SMTP_FROM=youraccount@gmail.com
NOTIFICATION_EMAIL=sir@example.com
TIMEZONE=Asia/Karachi
```

Do **not** put the Gmail password in React/frontend files.

For Gmail, use an **App Password** rather than your normal account password when the account supports App Passwords. Keep the App Password private.

## Example

If a session is saved as:

- Date: Monday
- Start: 7:00 PM
- End: 10:00 PM

NIAI sends:

**Subject:** `NIAI Attendance — AI / ML session has started`

The email includes the class name, course, date, start/end time, and a reminder to open NIAI Attendance.

If the saved session falls on Friday, Saturday, or Sunday, NIAI does not send that reminder.


## Teacher accounts and session workflow

- Teachers can create their own account from the Login / Sign up screen. New accounts are created with the `teacher` role.
- After login, a teacher can create, edit, or delete class sessions from **Class sessions**. The form includes class/session title, course, date, start time, and end time.
- Email reminders are sent at the session start time when SMTP is enabled. Friday, Saturday, and Sunday are skipped automatically.
- Set `NOTIFICATION_EMAIL` to the recipient (for example, the instructor's email). If it is blank, the logged-in teacher's email is used.
- Attendance results can be downloaded as CSV and printed from the result screen.

### Local run

Backend: `python -m uvicorn app.main:app --reload --port 8001`
Frontend: `npm run dev`

The frontend defaults to `http://localhost:8001` for the API.
