from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class BookingRequest(BaseModel):
    user_id: str = Field(examples=["usr_101"])
    trip_id: str = Field(examples=["trip_goa_4d"])
    seats: int = Field(default=1, ge=1, le=8)


class CheckoutRequest(BaseModel):
    booking_id: str
    payment_method_id: str
    amount: float = Field(gt=0)


class PaymentRequest(BaseModel):
    checkout_id: str
    payment_method_id: str
    amount: float = Field(gt=0)


class InventoryRequest(BaseModel):
    trip_id: str
    seats: int = Field(default=1, ge=1)


class NotificationRequest(BaseModel):
    user_id: str
    channel: str = Field(default="email")
    message: str


class ServiceResponse(BaseModel):
    status: str
    data: dict[str, Any]


class IncidentDemoResponse(BaseModel):
    scenario: str
    simulated_failure: dict[str, Any]
    triage_request: dict[str, Any]
    triage_report: dict[str, Any] | None

