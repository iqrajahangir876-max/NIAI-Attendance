# Deployment checklist

## Vercel
Deploy only `frontend/` as the Vercel project.
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_URL=https://YOUR-BACKEND-URL`
- Do not put JWT secrets, SMTP credentials, or database credentials in frontend variables.

## Render
Deploy `backend/` as a Docker Web Service, or use the included `render.yaml`.
The container binds to `0.0.0.0` and uses Render's `PORT` variable.
Set:
- DATABASE_URL
- JWT_SECRET
- CORS_ORIGINS=https://YOUR-VERCEL-DOMAIN
- SMTP_* if email reminders are enabled

Use managed PostgreSQL for production rather than SQLite.

## Production latency
- Keep the API process warm.
- Load OCR/native dependencies once when the container starts.
- Resize oversized images before OCR.
- Process only the register region after layout calibration.
- Avoid external LLM/API calls.
- For high traffic, add a worker queue; do not block the web process with long OCR jobs.
