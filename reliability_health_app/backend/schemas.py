"""Pydantic schemas for request validation and response serialization.

These models mirror the SQLAlchemy models defined in models.py but
they omit ORM-specific configuration and can nest other schemas as
appropriate. They are used by FastAPI to validate incoming payloads
and to ensure that responses adhere to the documented contract.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class TelemetryBase(BaseModel):
    metric_type: str = Field(..., example="HRV")
    value: float = Field(..., example=75.0)
    timestamp: Optional[datetime] = None
    payload: Optional[dict] = None


class TelemetryCreate(TelemetryBase):
    user_id: int


class TelemetryRead(TelemetryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    email: EmailStr
    baseline_hrv: Optional[float] = None
    baseline_rhr: Optional[float] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plain text password which will be hashed before storage")


class UserRead(UserBase):
    id: int
    created_at: datetime
    telemetry: List[TelemetryRead] = []

    class Config:
        orm_mode = True


class MealBase(BaseModel):
    name: str
    description: str
    category: Optional[str] = "global"


class MealCreate(MealBase):
    pass


class MealRead(MealBase):
    id: int

    class Config:
        orm_mode = True


class LabDataBase(BaseModel):
    apo_b: Optional[float] = None
    fasting_insulin: Optional[float] = None
    ferritin: Optional[float] = None
    timestamp: Optional[datetime] = None


class LabDataCreate(LabDataBase):
    user_id: int


class LabDataRead(LabDataBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class MicrobiomeBase(BaseModel):
    mitochondrial_health: Optional[float] = None
    oxidative_stress: Optional[float] = None
    butyrate_production: Optional[float] = None
    timestamp: Optional[datetime] = None


class MicrobiomeCreate(MicrobiomeBase):
    user_id: int


class MicrobiomeRead(MicrobiomeBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class ConsentBase(BaseModel):
    consent_given: bool = True
    timestamp: Optional[datetime] = None


class ConsentCreate(ConsentBase):
    user_id: int


class ConsentRead(ConsentBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str