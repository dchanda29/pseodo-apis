# Pseudo Commerce APIs

Lightweight demo APIs for showing how the Incident Triage AI agent integrates with an ongoing backend project.

This service simulates a small commerce/travel backend with booking, checkout, payments, inventory, and notification APIs. It can intentionally trigger realistic failures and call the Incident Triage AI backend to generate an AI-assisted root cause report.

## Why This Exists

The Incident Triage AI backend is easier to demo when there is an application producing business-level incidents.

This repo acts as that application:

```text
Pseudo Commerce APIs
        |
        | failure scenario
        v
Incident Triage AI Backend
        |
        v
AI triage report
```

## APIs

Business endpoints:

- `GET /health`
- `GET /services`
- `POST /bookings`
- `POST /checkout`
- `POST /payments/authorize`
- `POST /inventory/reserve`
- `POST /notifications/send`

Demo incident endpoints:

- `POST /demo/incidents/payment-failure`
- `POST /demo/incidents/checkout-degradation`
- `POST /demo/incidents/inventory-timeout`

## Local Setup

Install dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the pseudo APIs:

```bash
uvicorn pseudo_apis.main:app --reload --port 8010
```

Run the Incident Triage AI backend separately on port `8000`:

```bash
uvicorn incident_triage_ai.main:app --reload --port 8000
```

Trigger a demo incident:

```bash
curl -X POST http://127.0.0.1:8010/demo/incidents/payment-failure
```

## Environment Variables

```text
INCIDENT_TRIAGE_URL=http://127.0.0.1:8000
```

Set this to your deployed Incident Triage AI backend URL when hosting.

## Deployment

This repo includes a `render.yaml` blueprint for Render.

Set this environment variable on the deployed service:

```text
INCIDENT_TRIAGE_URL=https://your-incident-triage-backend.onrender.com
```

## Demo Flow

1. Start Incident Triage AI backend
2. Start this pseudo API service
3. Trigger `/demo/incidents/payment-failure`
4. Show the JSON response containing:
   - simulated service failure
   - affected business flow
   - triage request sent to the AI backend
   - AI-generated incident report

This gives you a clean LinkedIn/interview story:

> I built a demo commerce backend that generates realistic failures and automatically calls an AI incident triage service to produce root cause reports from logs, metrics, deployments, and runbooks.
