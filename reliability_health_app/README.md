# Reliability Engineer for Health Dashboard

This repository contains a minimal prototype of the **Reliability Engineer for Health** platform.  
The system is composed of a FastAPI backend and a simple HTML/JavaScript frontend.  
It demonstrates how raw health telemetry, nutritional templates and lab data can be ingested and analysed to produce actionable readiness states.

## Prerequisites

* Python 3.10+  
* `fastapi` and `uvicorn` must already be installed (they are part of this environment).  
* A modern web browser (Chrome/Firefox) to view the frontend.

### Optional Dependencies

* **SQLAlchemy & Postgres** – If you intend to use a Postgres database instead of the default SQLite, set the `DATABASE_URL` environment variable to something like `postgresql://user:password@host:5432/dbname` and ensure that `SQLAlchemy` and an appropriate driver (e.g. `psycopg2`) are installed in your Python environment.
* **Password/Token Libraries** – The built‑in authentication example uses SHA‑256 hashing and an in‑memory token store. For production deployments you should install `passlib` for secure password hashing and `python‑jose` for JWT token issuance.

If you wish to use the SQLAlchemy-backed backend, you will need to install `SQLAlchemy` separately.  
In this environment external package installation is disabled, so the provided example code refers to SQLAlchemy but cannot be run here without access to that dependency.

## Running the backend

To start the FastAPI server locally:

```bash
python -m reliability_health_app.backend.main
```

Alternatively you can run it via `uvicorn`:

```bash
uvicorn reliability_health_app.backend.main:app --reload
```

The server will listen on port 8000 by default.  
Upon startup it will populate the database with a handful of default meal templates.

### Database Configuration

The connection URL is read from the `DATABASE_URL` environment variable.  
If omitted the application defaults to `sqlite:///./health_app.db`. To use a Postgres instance instead, set `DATABASE_URL` accordingly before starting the server. For example:

```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/healthdb
uvicorn reliability_health_app.backend.main:app --reload
```

### Authentication

Users are created via the `/users/` endpoint with a name, email and password.  
Passwords are hashed using SHA‑256 before storage (not secure for production).  
Clients obtain a bearer token by POSTing to `/token` with form fields `username` (email) and `password`.  
Include this token in the `Authorization` header as `Bearer <token>` when calling protected endpoints such as `/telemetry/`, `/labs/`, `/microbiome/`, `/consent/`, `/readiness/{user_id}` and `/trends/{user_id}`.  
Tokens are stored in memory and will be lost when the server restarts.

### Trend Logic

The `compute_readiness_state` function now considers three metrics—heart rate variability (HRV), resting heart rate (RHR) and sleep duration.  
It uses personal baselines (if provided during user creation) or falls back to 30‑day averages. Deviations greater than 20% from baseline yield a **red** readiness state, deviations between 10–20% yield **yellow**, and lower deviations remain **green**.

### API Endpoints Overview

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/users/` | POST | Create a new user |
| `/users/` | GET | List users (with pagination) |
| `/users/{user_id}` | GET | Retrieve a specific user |
| `/telemetry/` | POST | Ingest a telemetry record |
| `/telemetry/users/{user_id}` | GET | Fetch telemetry for a user, filterable by metric and days |
| `/meals/` | GET | List available meal templates |
| `/meals/` | POST | Add a new meal template |
| `/labs/` | POST | Record lab results (ApoB, insulin, ferritin) |
| `/labs/users/{user_id}` | GET | Fetch a user's lab history |
| `/microbiome/` | POST | Record microbiome data |
| `/microbiome/users/{user_id}` | GET | Fetch a user's microbiome history |
| `/consent/` | POST | Capture a user's consent |
| `/consent/users/{user_id}/latest` | GET | Retrieve the most recent consent record |
| `/readiness/{user_id}` | GET | Compute the readiness state based on HRV and sleep trends |
| `/trends/{user_id}` | GET | Compute 7-day and 30-day averages for a metric |

## Running the frontend

The frontend is a single static HTML file that calls the FastAPI API via `fetch`.  
You don't need any build tools—simply open `frontend/index.html` in a web browser.  
Ensure the backend server is running at `http://localhost:8000` for API calls to succeed.

### Notes on a Richer UI

The provided HTML demonstrates only basic interactions. To build a more sophisticated dashboard with charts, meal configuration and workout management you may wish to use a front‑end framework like **React** or **Vue**. A skeleton structure for a React implementation (under `frontend-react/`) is included as a starting point. Since package installation is disabled in this environment, you should run `npm install` and `npm start` in your own environment to compile and serve the React app.

## Extending the system

* **Database:** Switch `DATABASE_URL` in `backend/database.py` to a Postgres URL and install SQLAlchemy to persist data more reliably.
* **Authentication:** Add user authentication and authorization using OAuth2 or JWT.
* **Trend logic:** Expand `crud.compute_readiness_state()` to incorporate additional metrics (e.g. resting heart rate, HRV deviations) and personal baselines.
* **Dashboard:** Build a richer frontend using a framework like React or Vue to visualise trends, configure meal rotations, and manage workouts.

## Disclaimer

This prototype is for demonstration purposes and is **not** intended for production use.  
Handling personal health information requires strict compliance with regulations (e.g. HIPAA) and robust security measures that are beyond the scope of this example.