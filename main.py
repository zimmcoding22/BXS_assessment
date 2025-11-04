from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, field_validator
import pandas as pd
import etl

app = FastAPI(title="BXS ETL API", version="1.0.0")

"""
Input validator for the POST /ingest route
Accepts either local file paths or s3:// URLs.
In a real prod flow you'd fetch from S3; for this exercise we allow local files.
"""
class IngestRequest(BaseModel):
    orders_url: str
    trades_url: str
    nbbo_url: str
    notes: Optional[str] = None
    @field_validator("orders_url", "trades_url", "nbbo_url")
    @classmethod
    def validate_path_or_s3(cls, v: str) -> str:
        # Allow local paths (data/*.csv) or s3://… (we'll treat s3 as not implemented here)
        if v.startswith("s3://"): return v  # Keep it. Error below if not implemented
        p = Path(v)
        if not p.exists(): raise ValueError(f"path does not exist: {v}")
        if p.suffix.lower() != ".csv": raise ValueError(f"expected a .csv file: {v}")
        return v

class IngestResponse(BaseModel):
    status: str
    output_files: Dict[str, str]
    rows: Dict[str, int]

class OrderSummary(BaseModel):
    order_id: str
    total_order_qty: int
    filled_qty: int
    vwap: float
    total_pi_dollars: float
    fill_rate: float

# Helpers
"""
If s3://… is provided, map it to a local file in ./data by filename. (Can swap this later to real S3 fetch using boto3.)
Otherwise treat as a filesystem path.
"""
def _localize_source(url_or_path: str) -> Path:
    if url_or_path.startswith("s3://"):
        # Map "s3://bucket/whatever/orders.csv" -> "data/orders.csv"
        fname = url_or_path.rstrip("/").split("/")[-1]
        p = Path("data") / fname
        if not p.exists(): raise HTTPException(status_code=422, detail=f"S3 URL given but local fixture not found: {p}. " f"Place a file named {fname} under ./data or implement S3 fetch.")
        return p
    return Path(url_or_path)

# API Routes
@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

"""
Runs the ETL using the provided sources.
Returns output filenames and simple row counts.
"""
@app.post("/ingest", response_model=IngestResponse)
def ingest(payload: IngestRequest) -> IngestResponse:
    try:
        orders_path = _localize_source(payload.orders_url)
        trades_path = _localize_source(payload.trades_url)
        nbbo_path = _localize_source(payload.nbbo_url)
        # call the small helper you’ll add in etl.py (see below)
        result = etl.run_etl_from_paths(orders_path=orders_path, trades_path=trades_path, nbbo_path=nbbo_path)
        return IngestResponse(status="ok", output_files={"fills": str(result["fills_path"]), "summary": str(result["summary_path"])}, rows=result["rows"])
    except Exception as exc: raise HTTPException(status_code=500, detail=f"ETL failed: {exc}") from exc

"""
Look up a single order’s summary metrics from the CSV produced by ETL.
"""
@app.get("/orders/{order_id}", response_model=OrderSummary)
def get_order(order_id: str) -> OrderSummary:
    summary_path = etl.OUTPUT_DIR / "order_summary.csv"
    if not summary_path.exists(): raise HTTPException(status_code=404, detail="order_summary.csv not found. Run /ingest first.")
    try: df = pd.read_csv(summary_path)
    except Exception as exc: raise HTTPException(status_code=500, detail=f"Failed to read summary: {exc}") from exc
    row = df.loc[df["order_id"] == order_id]
    if row.empty: raise HTTPException(status_code=404, detail=f"order_id not found: {order_id}")
    r = row.iloc[0] #only one row for summary
    return OrderSummary(order_id=str(r["order_id"]), total_order_qty=int(r["total_order_qty"]), filled_qty=int(r["filled_qty"]), vwap=float(r["vwap"]), total_pi_dollars=float(r["total_pi_dollars"]), fill_rate=float(r["fill_rate"]))
