"""CRUD utility functions for interacting with the database.

These helpers encapsulate common operations such as creating
resources or fetching records from the database. By keeping data
access logic separate from the FastAPI route handlers, we improve
maintainability and make the business logic easier to test.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas, auth


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # Hash the incoming password before storing it
    hashed = auth.hash_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed,
        baseline_hrv=user.baseline_hrv,
        baseline_rhr=user.baseline_rhr,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_telemetry(db: Session, telemetry: schemas.TelemetryCreate) -> models.Telemetry:
    db_record = models.Telemetry(
        user_id=telemetry.user_id,
        metric_type=telemetry.metric_type,
        value=telemetry.value,
        timestamp=telemetry.timestamp or datetime.utcnow(),
        payload=telemetry.payload,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_telemetry_by_user(db: Session, user_id: int, metric_type: Optional[str] = None, days: Optional[int] = None) -> List[models.Telemetry]:
    query = db.query(models.Telemetry).filter(models.Telemetry.user_id == user_id)
    if metric_type:
        query = query.filter(models.Telemetry.metric_type == metric_type)
    if days:
        start_time = datetime.utcnow() - timedelta(days=days)
        query = query.filter(models.Telemetry.timestamp >= start_time)
    return query.order_by(models.Telemetry.timestamp.desc()).all()


def calculate_rolling_average(records: List[models.Telemetry]) -> float:
    if not records:
        return 0.0
    total = sum(r.value for r in records)
    return total / len(records)


def create_meal(db: Session, meal: schemas.MealCreate) -> models.Meal:
    db_meal = models.Meal(name=meal.name, description=meal.description, category=meal.category)
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def get_meals(db: Session, skip: int = 0, limit: int = 100) -> List[models.Meal]:
    return db.query(models.Meal).offset(skip).limit(limit).all()


def create_lab_data(db: Session, lab: schemas.LabDataCreate) -> models.LabData:
    db_lab = models.LabData(
        user_id=lab.user_id,
        apo_b=lab.apo_b,
        fasting_insulin=lab.fasting_insulin,
        ferritin=lab.ferritin,
        timestamp=lab.timestamp or datetime.utcnow(),
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab


def get_lab_data_by_user(db: Session, user_id: int) -> List[models.LabData]:
    return db.query(models.LabData).filter(models.LabData.user_id == user_id).order_by(models.LabData.timestamp.desc()).all()


def create_microbiome_data(db: Session, data: schemas.MicrobiomeCreate) -> models.MicrobiomeData:
    db_micro = models.MicrobiomeData(
        user_id=data.user_id,
        mitochondrial_health=data.mitochondrial_health,
        oxidative_stress=data.oxidative_stress,
        butyrate_production=data.butyrate_production,
        timestamp=data.timestamp or datetime.utcnow(),
    )
    db.add(db_micro)
    db.commit()
    db.refresh(db_micro)
    return db_micro


def get_microbiome_by_user(db: Session, user_id: int) -> List[models.MicrobiomeData]:
    return db.query(models.MicrobiomeData).filter(models.MicrobiomeData.user_id == user_id).order_by(models.MicrobiomeData.timestamp.desc()).all()


def create_consent(db: Session, consent: schemas.ConsentCreate) -> models.Consent:
    db_consent = models.Consent(
        user_id=consent.user_id,
        consent_given=consent.consent_given,
        timestamp=consent.timestamp or datetime.utcnow(),
    )
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent


def get_latest_consent(db: Session, user_id: int) -> Optional[models.Consent]:
    return (
        db.query(models.Consent)
        .filter(models.Consent.user_id == user_id)
        .order_by(models.Consent.timestamp.desc())
        .first()
    )


def _readiness_recommendation(state: str) -> str:
    if state == "red":
        return "Recovery priority. Walk, mobility, hydration, and sleep protection today."
    if state == "yellow":
        return "Train, but reduce intensity. Avoid max-effort lifts or high-fatigue conditioning."
    return "Proceed with planned training. Strength and Zone 2 are acceptable today."


def compute_readiness_detail(db: Session, user_id: int) -> dict:
    """Return an explainable readiness decision payload.

    The API layer should not know about intermediate scoring variables.
    This function owns the calculation and returns the decision state,
    score, deviations, drivers, and recommended action as one contract.
    """
    user = get_user(db, user_id)
    if not user:
        state = "green"
        return {
            "user_id": user_id,
            "readiness_state": state,
            "score": 0,
            "hrv_dev": 0.0,
            "rhr_dev": 0.0,
            "sleep_dev": 0.0,
            "drivers": ["User not found; defaulting to green"],
            "recommendation": _readiness_recommendation(state),
        }

    hrv_7 = get_telemetry_by_user(db, user_id, metric_type="HRV", days=7)
    hrv_30 = get_telemetry_by_user(db, user_id, metric_type="HRV", days=30)
    rhr_7 = get_telemetry_by_user(db, user_id, metric_type="RHR", days=7)
    rhr_30 = get_telemetry_by_user(db, user_id, metric_type="RHR", days=30)
    sleep_7 = get_telemetry_by_user(db, user_id, metric_type="Sleep", days=7)
    sleep_30 = get_telemetry_by_user(db, user_id, metric_type="Sleep", days=30)

    avg_hrv_7 = calculate_rolling_average(hrv_7)
    avg_hrv_30 = calculate_rolling_average(hrv_30)
    avg_rhr_7 = calculate_rolling_average(rhr_7)
    avg_rhr_30 = calculate_rolling_average(rhr_30)
    avg_sleep_7 = calculate_rolling_average(sleep_7)
    avg_sleep_30 = calculate_rolling_average(sleep_30)

    baseline_hrv = user.baseline_hrv or avg_hrv_30 or avg_hrv_7
    baseline_rhr = user.baseline_rhr or avg_rhr_30 or avg_rhr_7
    baseline_sleep = avg_sleep_30 or avg_sleep_7

    if not hrv_7 or not rhr_7 or not sleep_7:
        state = "green"
        return {
            "user_id": user_id,
            "readiness_state": state,
            "score": 0,
            "hrv_dev": 0.0,
            "rhr_dev": 0.0,
            "sleep_dev": 0.0,
            "drivers": ["Insufficient 7-day telemetry; defaulting to green"],
            "recommendation": _readiness_recommendation(state),
        }

    if not baseline_hrv or not baseline_rhr or not baseline_sleep:
        state = "green"
        return {
            "user_id": user_id,
            "readiness_state": state,
            "score": 0,
            "hrv_dev": 0.0,
            "rhr_dev": 0.0,
            "sleep_dev": 0.0,
            "drivers": ["Insufficient baseline data; defaulting to green"],
            "recommendation": _readiness_recommendation(state),
        }

    hrv_dev = (baseline_hrv - avg_hrv_7) / baseline_hrv
    rhr_dev = (avg_rhr_7 - baseline_rhr) / baseline_rhr
    sleep_dev = (baseline_sleep - avg_sleep_7) / baseline_sleep

    score = 0
    drivers = []

    if hrv_dev > 0.10:
        score += 2
        drivers.append("HRV suppressed more than 10% from baseline")
    elif hrv_dev > 0.05:
        score += 1
        drivers.append("HRV mildly suppressed from baseline")

    if rhr_dev > 0.10:
        score += 2
        drivers.append("Resting heart rate elevated more than 10% from baseline")
    elif rhr_dev > 0.05:
        score += 1
        drivers.append("Resting heart rate mildly elevated from baseline")

    if sleep_dev > 0.10:
        score += 2
        drivers.append("Sleep reduced more than 10% from baseline")
    elif sleep_dev > 0.05:
        score += 1
        drivers.append("Sleep mildly reduced from baseline")

    if score >= 4:
        state = "red"
    elif score >= 2:
        state = "yellow"
    else:
        state = "green"

    return {
        "user_id": user_id,
        "readiness_state": state,
        "score": score,
        "hrv_dev": round(hrv_dev, 3),
        "rhr_dev": round(rhr_dev, 3),
        "sleep_dev": round(sleep_dev, 3),
        "drivers": drivers,
        "recommendation": _readiness_recommendation(state),
    }


def compute_readiness_state(db: Session, user_id: int) -> str:
    """Backward-compatible readiness state helper."""
    return compute_readiness_detail(db, user_id)["readiness_state"]
