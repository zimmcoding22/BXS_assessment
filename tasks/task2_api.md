# Task 2 — API (FastAPI)

**Goal:** Expose a small REST API with FastAPI that:
- `POST /ingest` — accepts a JSON payload with file paths/URLs (see `api/mock_payload.json`) and runs your ETL.
- `GET /orders/{order_id}` — returns order-level summary metrics computed in Task 1.
- `GET /health` — returns `{status: "ok"}`.

**Requirements:**
- Validate input with Pydantic models.
- Return helpful errors.
- Include a `README` snippet showing how to run locally (`uvicorn main:app --reload`).