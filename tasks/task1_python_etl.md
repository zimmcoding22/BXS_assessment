# Task 1 — Python ETL (Orders/Trades/NBBO)

**Goal:** Build a Python script (`etl.py`) that ingests `data/orders_sample.csv`, `data/trades_sample.csv`, and `data/nbbo_sample.csv` and produces:
1. A **normalized fills** dataset (Parquet or CSV) that joins trades to orders and aligns each trade with the **closest prior NBBO snapshot** by symbol/timestamp.
2. **Execution-quality metrics** per trade and per order:
   - Price improvement (PI) per share for BUY = max(0, NBBO_ask - exec_price); for SELL = max(0, exec_price - NBBO_bid).
   - Total PI dollars = PI_per_share × exec_quantity.
   - Slippage vs. order limit price.
3. An **order-level summary** file with: total quantity, filled quantity, VWAP, total PI dollars, and fill rate.

**Constraints & evaluation:**
- Process should handle **large files** by streaming/chunking (show how you'd scale beyond memory).
- Use **type hints**, clear logging, and docstrings.
- Include a minimal **unit test** (`tests/test_etl.py`) that validates PI math on a small fixture.
