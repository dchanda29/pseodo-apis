from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from httpx import HTTPError

from pseudo_apis.config import settings
from pseudo_apis.incident_client import IncidentTriageClient
from pseudo_apis.models import (
    BookingRequest,
    CheckoutRequest,
    IncidentDemoResponse,
    InventoryRequest,
    NotificationRequest,
    PaymentRequest,
    ServiceResponse,
    Severity,
)

app = FastAPI(
    title=settings.app_name,
    description="Pseudo business APIs that integrate with Incident Triage AI for demos.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

incident_client = IncidentTriageClient()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name, "environment": settings.app_env}


@app.get("/services")
def services() -> dict[str, list[str]]:
    return {
        "services": [
            "booking-api",
            "checkout-api",
            "payments-api",
            "inventory-api",
            "notifications-api",
        ]
    }


@app.post("/bookings", response_model=ServiceResponse)
def create_booking(request: BookingRequest) -> ServiceResponse:
    return ServiceResponse(
        status="confirmed",
        data={
            "booking_id": f"bkg_{uuid4().hex[:10]}",
            "user_id": request.user_id,
            "trip_id": request.trip_id,
            "seats": request.seats,
        },
    )


@app.post("/checkout", response_model=ServiceResponse)
def create_checkout(request: CheckoutRequest) -> ServiceResponse:
    return ServiceResponse(
        status="payment_required",
        data={
            "checkout_id": f"chk_{uuid4().hex[:10]}",
            "booking_id": request.booking_id,
            "amount": request.amount,
            "next_step": "POST /payments/authorize",
        },
    )


@app.post("/payments/authorize", response_model=ServiceResponse)
def authorize_payment(request: PaymentRequest) -> ServiceResponse:
    return ServiceResponse(
        status="authorized",
        data={
            "payment_id": f"pay_{uuid4().hex[:10]}",
            "checkout_id": request.checkout_id,
            "amount": request.amount,
        },
    )


@app.post("/inventory/reserve", response_model=ServiceResponse)
def reserve_inventory(request: InventoryRequest) -> ServiceResponse:
    return ServiceResponse(
        status="reserved",
        data={
            "reservation_id": f"res_{uuid4().hex[:10]}",
            "trip_id": request.trip_id,
            "seats": request.seats,
        },
    )


@app.post("/notifications/send", response_model=ServiceResponse)
def send_notification(request: NotificationRequest) -> ServiceResponse:
    return ServiceResponse(
        status="queued",
        data={
            "notification_id": f"ntf_{uuid4().hex[:10]}",
            "user_id": request.user_id,
            "channel": request.channel,
        },
    )


@app.post("/demo/incidents/payment-failure", response_model=IncidentDemoResponse)
async def demo_payment_failure() -> IncidentDemoResponse:
    return await _trigger_demo_incident(
        scenario="payment-failure",
        service="payments-api",
        severity=Severity.high,
        question="Why are payments failing after the latest deployment?",
        simulated_failure={
            "business_flow": "booking checkout",
            "endpoint": "POST /payments/authorize",
            "status_code": 500,
            "error": "Payment provider credential validation failed",
            "trace_id": "demo_pay_001",
        },
    )


@app.post("/demo/incidents/checkout-degradation", response_model=IncidentDemoResponse)
async def demo_checkout_degradation() -> IncidentDemoResponse:
    return await _trigger_demo_incident(
        scenario="checkout-degradation",
        service="checkout-api",
        severity=Severity.critical,
        question="Checkout has many 500 errors and payment failures",
        simulated_failure={
            "business_flow": "checkout",
            "endpoint": "POST /checkout",
            "status_code": 503,
            "error": "Upstream payments-api returned repeated 500 responses",
            "trace_id": "demo_chk_001",
        },
    )


@app.post("/demo/incidents/inventory-timeout", response_model=IncidentDemoResponse)
async def demo_inventory_timeout() -> IncidentDemoResponse:
    return await _trigger_demo_incident(
        scenario="inventory-timeout",
        service="inventory-api",
        severity=Severity.medium,
        question="Why is inventory reservation timing out during booking?",
        simulated_failure={
            "business_flow": "booking inventory reservation",
            "endpoint": "POST /inventory/reserve",
            "status_code": 504,
            "error": "Inventory reservation timed out waiting for database response",
            "trace_id": "demo_inv_001",
        },
    )


async def _trigger_demo_incident(
    *,
    scenario: str,
    service: str,
    severity: Severity,
    question: str,
    simulated_failure: dict[str, object],
) -> IncidentDemoResponse:
    triage_request = {
        "question": question,
        "service": service,
        "severity": severity.value,
    }

    try:
        triage_report = await incident_client.analyze(
            question=question,
            service=service,
            severity=severity,
        )
    except HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Incident Triage AI backend is unavailable: {exc}",
        ) from exc

    return IncidentDemoResponse(
        scenario=scenario,
        simulated_failure=simulated_failure,
        triage_request=triage_request,
        triage_report=triage_report,
    )
