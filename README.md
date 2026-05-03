# Reliability Engineer for Health

## Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn reliability_health_app.backend.main:app --reload
```

API runs at:
http://127.0.0.1:8000/docs

---

## Frontend (React)

```bash
cd frontend-react
npm install
npm run dev
```

Runs at:
http://localhost:5173

---

## Environment

Create `.env` in frontend-react:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## Flow

1. Create user via Swagger
2. Login → get token
3. Use token in frontend
4. Submit telemetry
5. View readiness decision

---

## System Concept

This system is not a fitness tracker.

It is a **decision engine**:

- Inputs → HRV, RHR, Sleep
- Processing → deviation + scoring
- Output → readiness + drivers + recommendation

"Trust Through Evidence"
