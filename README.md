# BXS DevOps Candidate Exercise (Core)

**What we assess:** Python quality, large-data handling, API design, DB skills, Git/GitHub workflow, front‑end basics (React.js), and AWS S3 familiarity.

## Deliverables
- `etl.py` and `tests/test_etl.py` (Task 1)
- `main.py` (FastAPI) (Task 2)
- `load_db.py` + brief schema/index notes (Task 3)
- `.github/workflows/ci.yml` + `CONTRIBUTING.md` (Task 4)
- `/frontend/` React.js app (Task 6)
- `s3_utils.py` and usage notes (Task 7)

## Data
Sample CSVs live in `data/`. Treat them as if they were large files (demonstrate chunking/streaming patterns).

## How to run (example)
- ETL: `python etl.py`
- API: `uvicorn main:app --reload`
- DB load: `python load_db.py`
- Front-end: `cd frontend && npm install && npm run dev`

## Scoring Rubric (95 pts)
- **Python ETL (35 pts):** correctness of joins & metrics, chunked processing, tests, logging/type hints.
- **API (20 pts):** input validation, endpoints, error handling, README clarity.
- **Database (15 pts):** schema/indexes, idempotency, example queries.
- **GitHub/CI (10 pts):** lint/tests pass, clear PR workflow.
- **React.js Front-End (5 pts):** basic fetch/render from API, clean hooks/state.
- **AWS S3 (10 pts):** upload/list, security, setup notes.

## Submission
- Send a GitHub repo link or a zip. Include a short `DECISIONS.md` explaining assumptions and trade‑offs.

## Notes
- Use env vars or secrets for credentials; do **not** hard-code.
- Keep dependencies minimal (see `requirements.txt`).


----------------------------------------------------------------

## Task 2 — API (FastAPI)

This task exposes a small REST API using FastAPI with the following endpoints:
- `POST /ingest` — accepts file paths or URLs and runs the ETL process.
- `GET /orders/{order_id}` — returns summary metrics computed in Task 1.
- `GET /health` — returns `{status: "ok"}`.

### Run Locally

To start the FastAPI server locally and test endpoints:

```bash
uvicorn main:app --reload

Example successful requests

#check health
-curl -X GET http://127.0.0.1:8000/health response: {"status": "ok"}
#trigger ETL pipe
-curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "orders_url": "data/orders_sample.csv",
        "trades_url": "data/trades_sample.csv",
        "nbbo_url": "data/nbbo_sample.csv"
      }' 
response:
{
  "status": "ok",
  "output_files": {
    "fills": "output/fills_normalized.csv",
    "summary": "output/order_summary.csv"
  },
  "rows": {
    "fills": 10000,
    "summary": 50
  }
}
#specific order summary
-curl -X GET http://127.0.0.1:8000/orders/O00011 
response: 
{
  "order_id": "O00011",
  "total_order_qty": 1463,
  "filled_qty": 1463,
  "vwap": 98.85,
  "total_pi_dollars": 407079.75,
  "fill_rate": 1.0
}


## Task 3 — Database Persistence (MongoDB)

Create a free cluster on https://cloud.mongodb.com/

**using cloud to avoid local download issues for myself as well as whoever is testing.

MONGO_URI="mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.xxxxx.mongodb.net/?appName=Cluster0"

- Create a database user, and replace the Mongo URI above with the generated string, username, and password
- Allow all hosts or restrict to specific IPs if necessary
- run python load_db.py using the generated URI and db





