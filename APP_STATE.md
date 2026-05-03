# Workout Align / Reliability Health App — Current State

## Backend status
- FastAPI backend runs at http://127.0.0.1:8000
- Swagger docs available at http://127.0.0.1:8000/docs
- SQLite database: health_app.db
- Auth upgraded from in-memory tokens to JWT
- Password hashing uses passlib + bcrypt
- bcrypt pinned to 4.0.1 due passlib compatibility

## Working endpoints
- POST /users/
- POST /token
- POST /telemetry/
- GET /readiness/{user_id}
- GET /trends/{user_id}
- GET /meals/

## Current readiness model
- Uses 7-day HRV, RHR, and Sleep averages
- Uses user baseline HRV/RHR or 30-day fallback
- Weighted score:
  - HRV deviation > 10% = +2, > 5% = +1
  - RHR deviation > 10% = +2, > 5% = +1
  - Sleep deviation > 10% = +2, > 5% = +1
- score >= 4 = red
- score >= 2 = yellow
- else green

## Known issue / next refactor
- main.py should not directly reference score/hrv_dev/rhr_dev/sleep_dev
- Add crud.compute_readiness_detail()
- Then have GET /readiness/{user_id} return the full readiness payload

## Startup command
source .venv/bin/activate
python -m uvicorn reliability_health_app.backend.main:app --reload

## Dependency pin recommendation
passlib==1.7.4
bcrypt==4.0.1
python-jose==3.5.0
