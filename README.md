# NIAI Attendance

Low-latency attendance-register digitization system.

Flow:
Register image/PDF -> OpenCV preprocessing -> OCR -> table/mark parsing -> reviewable attendance -> CSV/print -> analytics.

No LLM API is required.

## Stack
- Frontend: React + TypeScript + Vite + Framer Motion
- Backend: Python + FastAPI + SQLAlchemy
- CV/OCR: OpenCV + Tesseract + PyMuPDF
- Auth: JWT + bcrypt, roles: admin / teacher
- Local DB: SQLite; production-ready DB URL for PostgreSQL
- Docker: backend + frontend
- Deployment: Vercel frontend, Render/Docker backend

## Important
The parser is a generic baseline. Attendance registers differ in grid layout, handwriting, symbols, scan quality, and languages. Test against your actual register and tune the parser before claiming production accuracy.

## Local prerequisites
- Python 3.11
- Node.js 20+
- Tesseract OCR installed and available on PATH
- Docker Desktop (optional)

## 1. Backend
Windows PowerShell:
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

Demo users:
- admin@example.com / Admin123!
- teacher@example.com / Teacher123!

## 2. Frontend
```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```
Open http://localhost:5173

## 3. Docker
From the project root:
```powershell
docker compose up --build
```
Frontend: http://localhost:5173
Backend: http://localhost:8000

## 4. Accuracy workflow
1. Upload 5-10 representative register pages.
2. Compare OCR names/dates/statuses with the original.
3. Tune row/column detection and status normalization in:
   backend/app/services/register_parser.py
4. Keep uncertain cells marked for teacher review.
5. Measure precision/recall on a held-out sample before presenting accuracy.

## 5. Production
Frontend -> Vercel.
Backend -> Render Docker Web Service or another persistent container host.
PostgreSQL -> managed Postgres.
Set CORS, JWT_SECRET, DATABASE_URL, SMTP settings and API URL in environment variables.
Never commit .env, credentials, uploads, or database files.
