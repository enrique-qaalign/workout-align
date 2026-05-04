"""Main FastAPI application for the Reliability Engineer for Health platform.

This module wires together the database, schemas, and CRUD
operations into a fully-functional REST API. Endpoints cover user
management, telemetry ingestion, meal templates, lab results,
microbiome data, consent records, and readiness state computation.

To run the server locally, execute:

    uvicorn reliability_health_app.backend.main:app --reload

"""

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from . import models, schemas, crud, auth
from .database import SessionLocal, engine, Base

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reliability Engineer for Health API", version="0.1")

# Allow cross-origin requests from the frontend running on a separate port
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Populate default meal templates on startup if the table is empty
@app.on_event("startup")
def startup_populate_defaults() -> None:
    db = SessionLocal()
    try:
        meal_count = db.query(models.Meal).count()
        if meal_count == 0:
            defaults = [
                {
                    "name": "Rustic Italian",
                    "description": "Wide pasta with turkey and lean Italian sausage blend",
                    "category": "rustic_italian",
                },
                {
                    "name": "Modern Steakhouse",
                    "description": "6 oz filet or sirloin with garlic rosemary baby potatoes",
                    "category": "modern_steakhouse",
                },
                {
                    "name": "Tuscan Coastal",
                    "description": "Pan-seared salmon with lemon farro",
                    "category": "tuscan_coastal",
                },
                {
                    "name": "Cozy Stromboli",
                    "description": "Thin-crust engineered stromboli with lean turkey and mozzarella",
                    "category": "cozy_stromboli",
                },
                {
                    "name": "California Brunch-for-Dinner",
                    "description": "California scramble with avocado and roasted sweet potatoes",
                    "category": "california_brunch",
                },
            ]
            for meal in defaults:
                crud.create_meal(db, schemas.MealCreate(**meal))
    finally:
        db.close()


def get_db():
    """Provide a database session per request and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Set up OAuth2 bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """Dependency that returns the current user based on a bearer token."""
    user_id = auth.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


# Users endpoints
@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Authentication endpoint
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticate a user and return an access token.

    Clients should send a form with `username` and `password`. The
    returned token can be supplied in the `Authorization` header as
    `Bearer <token>` for subsequent requests to protected endpoints.
    """
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = auth.create_access_token(user_id=user.id)
    return schemas.Token(access_token=token, token_type="bearer")


# Telemetry endpoints
@app.post("/telemetry/", response_model=schemas.TelemetryRead)
def create_telemetry_record(
    telemetry: schemas.TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Ensure the token belongs to the user whose data is being written
    if current_user.id != telemetry.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit telemetry for another user")
    return crud.create_telemetry(db=db, telemetry=telemetry)


@app.get("/telemetry/users/{user_id}", response_model=List[schemas.TelemetryRead])
def read_user_telemetry(
    user_id: int,
    metric_type: Optional[str] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view telemetry for another user")
    return crud.get_telemetry_by_user(db, user_id=user_id, metric_type=metric_type, days=days)


# Meal endpoints
@app.get("/meals/", response_model=List[schemas.MealRead])
def read_meals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_meals(db, skip=skip, limit=limit)


@app.post("/meals/", response_model=schemas.MealRead)
def create_meal(
    meal: schemas.MealCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # In a real application, check for admin privileges here
    return crud.create_meal(db=db, meal=meal)


# Lab data endpoints
@app.post("/labs/", response_model=schemas.LabDataRead)
def create_lab_record(
    lab: schemas.LabDataCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != lab.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit lab data for another user")
    return crud.create_lab_data(db=db, lab=lab)


@app.get("/labs/users/{user_id}", response_model=List[schemas.LabDataRead])
def read_lab_records(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view lab data for another user")
    return crud.get_lab_data_by_user(db, user_id=user_id)


# Microbiome data endpoints
@app.post("/microbiome/", response_model=schemas.MicrobiomeRead)
def create_microbiome_record(
    data: schemas.MicrobiomeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != data.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit microbiome data for another user")
    return crud.create_microbiome_data(db=db, data=data)


@app.get("/microbiome/users/{user_id}", response_model=List[schemas.MicrobiomeRead])
def read_microbiome_records(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view microbiome data for another user")
    return crud.get_microbiome_by_user(db, user_id=user_id)


# Consent endpoints
@app.post("/consent/", response_model=schemas.ConsentRead)
def create_consent_record(
    consent: schemas.ConsentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != consent.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit consent for another user")
    return crud.create_consent(db=db, consent=consent)


@app.get("/consent/users/{user_id}/latest", response_model=schemas.ConsentRead)
def read_latest_consent(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view consent for another user")
    record = crud.get_latest_consent(db, user_id=user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Consent record not found")
    return record


# Readiness endpoint
@app.get("/readiness/{user_id}")
def get_readiness_state(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view readiness for another user")
    return crud.compute_readiness_detail(db, user_id=user_id)


# Trend endpoint (rolling averages)
@app.get("/trends/{user_id}")
def get_trends(
    user_id: int,
    metric_type: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return the 7-day and 30-day rolling averages for a given metric."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view trends for another user")
    records_7 = crud.get_telemetry_by_user(db, user_id=user_id, metric_type=metric_type, days=7)
    records_30 = crud.get_telemetry_by_user(db, user_id=user_id, metric_type=metric_type, days=30)
    avg_7 = crud.calculate_rolling_average(records_7)
    avg_30 = crud.calculate_rolling_average(records_30)
    return {
        "user_id": user_id,
        "metric_type": metric_type,
        "average_7_day": avg_7,
        "average_30_day": avg_30,
    }
