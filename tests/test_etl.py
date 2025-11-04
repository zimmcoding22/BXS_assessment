import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from pathlib import Path
import pytest
from etl import load_nbbo, load_orders, process_trades_in_chunks, run_etl, OUTPUT_DIR

"""
Fixture to load NBBO data once per test session.
"""
@pytest.fixture(scope="module")
def nbbo_df():
    return load_nbbo()

"""
Fixture to load Orders data once per test session.
"""
@pytest.fixture(scope="module")
def orders_df():
    return load_orders()

"""
NBBO data should not be empty and must contain key columns.
"""
def test_load_nbbo(nbbo_df):
    assert not nbbo_df.empty
    for col in ["symbol", "timestamp", "bid", "ask"]:
        assert col in nbbo_df.columns

"""
Orders data should not be empty and contain timestamp and order_id.
"""
def test_load_orders(orders_df):
    assert not orders_df.empty
    assert "order_id" in orders_df.columns
    assert "timestamp" in orders_df.columns

"""
Each processed trade chunk should align with NBBO correctly.
"""
def test_process_chunk_alignment(nbbo_df, orders_df):
    # Run only one chunk for speed
    chunk_iter = process_trades_in_chunks(nbbo_df, orders_df)
    first_chunk = next(chunk_iter)
    # Ensure required metrics were computed
    for col in ["pi_per_share", "pi_dollars", "slippage"]:
        assert col in first_chunk.columns
    assert (first_chunk["timestamp_y"] <= first_chunk["exec_timestamp"]).all() # Verify NBBO timestamp <= trade exec_timestamp

"""
ETL run should create both output CSVs.
"""
def test_run_etl_creates_outputs():
    run_etl()
    fills_path = OUTPUT_DIR / "fills_normalized.csv"
    summary_path = OUTPUT_DIR / "order_summary.csv"
    assert fills_path.exists()
    assert summary_path.exists()
    fills = pd.read_csv(fills_path)
    summary = pd.read_csv(summary_path)
    # Sanity checks on output structure
    assert {"order_id", "exec_price", "pi_dollars"}.issubset(fills.columns)
    assert {"order_id", "fill_rate", "total_pi_dollars"}.issubset(summary.columns)
