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


def compute_readiness_state(db: Session, user_id: int) -> str:
    """Compute a readiness state based on HRV, resting heart rate and sleep.

    The algorithm calculates 7‑day averages for HRV, resting heart
    rate (RHR) and sleep metrics. It then determines personal
    baselines from the user's stored preferences (if available) or
    falls back to 30‑day averages. Deviations from baseline are
    computed as a percentage. A large negative deviation in HRV or
    sleep—or a large positive deviation in RHR—indicates reduced
    readiness.

    Thresholds:
      * deviation > 0.2 → red (significant stress or fatigue)
      * deviation > 0.1 → yellow (moderate stress)
      * otherwise → green
    """
    user = get_user(db, user_id)
    if not user:
        return "green"

    # Fetch 7‑day and 30‑day telemetry for HRV, RHR and Sleep
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

    # Determine baselines: use user-defined baselines if present; otherwise 30‑day average
    baseline_hrv = user.baseline_hrv or avg_hrv_30 or avg_hrv_7
    baseline_rhr = user.baseline_rhr or avg_rhr_30 or avg_rhr_7
    baseline_sleep = avg_sleep_30 or avg_sleep_7

    if baseline_hrv == 0 or baseline_rhr == 0 or baseline_sleep == 0:
        return "green"
    

    # Deviations: negative values for HRV and sleep (lower than baseline) indicate fatigue; positive values for RHR (higher than baseline) indicate stress.
    if not hrv_7 or not rhr_7 or not sleep_7:
        return "green"
    if not baseline_hrv or not baseline_rhr or not baseline_sleep:
        return "green"
    hrv_dev = (baseline_hrv - avg_hrv_7) / baseline_hrv
    rhr_dev = (avg_rhr_7 - baseline_rhr) / baseline_rhr
    sleep_dev = (baseline_sleep - avg_sleep_7) / baseline_sleep


    # Choose the worst deviation. Only positive deviations matter; negative rhr_dev indicates lower RHR which is positive.
    deviations = [d for d in (hrv_dev, rhr_dev, sleep_dev) if d > 0]
    score = 0

    # HRV (most important)
    if hrv_dev > 0.1:
        score += 2
    elif hrv_dev > 0.05:
        score += 1

    # RHR
    if rhr_dev > 0.1:
        score += 2
    elif rhr_dev > 0.05:
        score += 1

    # Sleep
    if sleep_dev > 0.1:
        score += 2
    elif sleep_dev > 0.05:
        score += 1
    print({
        "hrv_dev": hrv_dev,
        "rhr_dev": rhr_dev,
        "sleep_dev": sleep_dev,
        "score": score
        })

    if score >= 4:
        return "red"
    elif score >= 2:
        return "yellow"
    else:
        return "green"