# Task 3 — Database

**Goal:** Persist outputs to a database of your choice:
- Use **MongoDB** (preferred) or **SQLite**.
- Collections/tables:
  - `orders` (order-level aggregates)
  - `trades` (trade-level with PI metrics)
- Provide simple indexes (e.g., `order_id`, `symbol`, `exec_timestamp`).
- Include a script `load_db.py` and instructions to run it.

**Evaluation:** schema clarity, indexing choices, idempotent loads, and basic query examples (e.g., top 5 orders by PI).