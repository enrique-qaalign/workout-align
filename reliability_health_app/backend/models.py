"""SQLAlchemy ORM models defining the database schema for the
Reliability Engineer for Health platform.

These models represent users, telemetry data, nutritional options,
laboratory results, microbiome readings, and consent records. They
provide a flexible structure that can be extended to support new
features or additional health metrics without requiring disruptive
schema changes.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """A registered user of the health platform.

    Users represent individuals whose telemetry and lab data are being
    tracked. For simplicity, this model stores only basic
    demographic information. Additional user preferences and
    configuration options can be stored in separate tables or as
    JSON-encoded fields depending on future requirements.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Store hashed password instead of plain text for security
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Personal baseline metrics for readiness calculations (optional). If
    # provided by the user or clinician, these values will be used to
    # determine deviations instead of the 30‑day rolling average.
    baseline_hrv = Column(Float, nullable=True)
    baseline_rhr = Column(Float, nullable=True)

    # Relationships
    telemetry = relationship("Telemetry", back_populates="user", cascade="all, delete-orphan")
    lab_results = relationship("LabData", back_populates="user", cascade="all, delete-orphan")
    microbiome_results = relationship("MicrobiomeData", back_populates="user", cascade="all, delete-orphan")
    consent_records = relationship("Consent", back_populates="user", cascade="all, delete-orphan")


class Telemetry(Base):
    """Raw time-series data ingested from wearables like Apple Watch.

    Each telemetry record captures a single measurement of a health
    metric (e.g. HRV, resting heart rate, sleep stage). The value
    field is stored as a float; additional metadata can be stored in
    the optional payload field as JSON if needed for more complex
    measurements.
    """

    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String, index=True)  # e.g. HRV, RHR, Sleep, SpO2
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    payload = Column(JSON, nullable=True)

    user = relationship("User", back_populates="telemetry")


class Meal(Base):
    """Meal templates used to structure nutrition guidance.

    A meal defines a signature dish that users can select as part of
    their weekly rotation. The schema is intentionally minimal but
    can be extended to include nutritional macros, ingredient lists,
    or associations with specific days of the Sovereign Week.
    """

    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, default="global")  # e.g. rustic_italian, modern_steakhouse, etc.


class LabData(Base):
    """Periodic clinical laboratory results provided by external labs.

    This table stores key blood markers such as ApoB, fasting insulin
    and ferritin. Additional metrics can be added as nullable columns
    or grouped into a JSON payload depending on the anticipated
    flexibility required.
    """

    __tablename__ = "lab_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    apo_b = Column(Float, nullable=True)
    fasting_insulin = Column(Float, nullable=True)
    ferritin = Column(Float, nullable=True)

    user = relationship("User", back_populates="lab_results")


class MicrobiomeData(Base):
    """Microbiome and gene expression readings.

    Stores three high-level dimensions of gut health and cellular
    function that can influence training and nutrition recommendations.
    Values are nullable floats representing relative expression levels
    or scores returned by third-party services like Viome.
    """

    __tablename__ = "microbiome_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    mitochondrial_health = Column(Float, nullable=True)
    oxidative_stress = Column(Float, nullable=True)
    butyrate_production = Column(Float, nullable=True)

    user = relationship("User", back_populates="microbiome_results")


class Consent(Base):
    """User consent records for handling protected health information.

    Each consent entry captures whether the user has agreed to data
    collection and processing, along with the time of consent. This
    audit trail supports compliance with HIPAA and other regulatory
    frameworks.
    """

    __tablename__ = "consent"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consent_given = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="consent_records")