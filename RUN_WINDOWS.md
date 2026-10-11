# NIAI Attendance — Windows Quick Start

## 1. Requirements
- Python 3.10+
- Node.js 18+
- Tesseract OCR installed and available as `tesseract` in PowerShell

## 2. Backend (PowerShell window 1)
```powershell
cd "C:\path\to\NIAI-Attendance\backend"
if (!(Test-Path .venv)) { python -m venv .venv }
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.seed
python -m uvicorn app.main:app --reload --port 8001
```
Keep this window open. Backend health: http://127.0.0.1:8001/health

## 3. Frontend (PowerShell window 2)
```powershell
cd "C:\path\to\NIAI-Attendance\frontend"
npm install
npm run dev
```
Open: http://localhost:5173

## 4. Demo login
- Teacher: `teacher@example.com` / `Teacher123!`
- Admin: `admin@example.com` / `Admin123!`

## 5. Teacher flow
1. Sign up or use the demo teacher account.
2. Open **Class sessions** and create a session (course, date, start/end time).
3. Dashboard → **Manual attendance** → select the session → mark P/A/L for each student.
4. **Scan register** → upload JPG/PNG/WEBP/PDF. PDF pages are rasterized and processed one-by-one with OpenCV + Tesseract.
5. Use **CSV** or **Print** on the scan result.

## 6. Email reminder
Email is disabled by default. To enable it, edit `backend/.env`:
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
The scheduler checks every 15 seconds and sends at the session start time. Friday, Saturday and Sunday reminders are skipped.

## 7. If the browser says “Failed to fetch”
- Make sure backend window is still running on port **8001**.
- Open http://127.0.0.1:8001/health and confirm `ok: true`.
- Confirm `frontend/.env` contains `VITE_API_URL=http://localhost:8001`.
- Restart Vite after changing `.env`.

## 8. Important OCR note
The supplied register is a scanned handwritten CamScanner PDF. OCR is intentionally implemented without an LLM API, but handwriting can produce uncertain names/marks. The app exposes OCR results for review rather than silently pretending uncertain cells are correct.
