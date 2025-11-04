import pandas as pd
import numpy as np
from pathlib import Path
from typing import Iterator

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
ORDERS_PATH = DATA_DIR / "orders_sample.csv"
TRADES_PATH = DATA_DIR / "trades_sample.csv"
NBBO_PATH = DATA_DIR / "nbbo_sample.csv"
CHUNK_SIZE = 5000 #arbitrary

"""
Load NBBO snapshots sorted by symbol/timestamp.
Returns: pd.DataFrame: NBBO data sorted by symbol and timestamp.
"""
def load_nbbo() -> pd.DataFrame:
    nbbo = pd.read_csv(NBBO_PATH, parse_dates=["timestamp"])
    nbbo.sort_values(["symbol", "timestamp"], inplace=True)
    return nbbo

"""
Load orders.
Returns: pd.DataFrame: Orders data with parsed timestamps.
"""
def load_orders() -> pd.DataFrame:
    orders = pd.read_csv(ORDERS_PATH, parse_dates=["timestamp"])
    return orders

"""
Process trades with metrics. Yield in successive chunks rather than loading full data set at once because large data sets cannot be loaded into RAM
arg nbbo (pd.DataFrame): NBBO quotes data sorted by symbol and timestamp.
arg orders (pd.DataFrame): Orders data with order IDs and limit prices.
Yields pd.DataFrame: A processed chunk containing trades joined with NBBO and calculated metrics.
"""
def process_trades_in_chunks(nbbo: pd.DataFrame, orders: pd.DataFrame) -> Iterator[pd.DataFrame]:
    for chunk in pd.read_csv(TRADES_PATH, parse_dates=["exec_timestamp"], chunksize=CHUNK_SIZE):
        print(f"Processing trade chunk with {len(chunk)} rows")
        # Merge trades and orders
        merged = chunk.merge(orders, on="order_id", suffixes=("_trade", "_order")) #suffixes make it clear in column headers which data set the field came from
        print("Merged columns:", merged.columns.tolist())
        # Rename so both sides have the same join column
        merged.rename(columns={"symbol_trade": "symbol"}, inplace=True)
        # Sort and reset index for merge_asof
        merged = merged.sort_values(["exec_timestamp", "symbol"], kind="mergesort").reset_index(drop=True)
        nbbo = nbbo.sort_values(["timestamp", "symbol"], kind="mergesort").reset_index(drop=True)
        aligned = pd.merge_asof(merged, nbbo, by="symbol", left_on="exec_timestamp", right_on="timestamp", direction="backward") # Merge_asof aligns each trade with the latest NBBO before its timestamp
        # Compute metrics
        aligned["pi_per_share"] = np.where(aligned["side_trade"] == "BUY", np.maximum(0, aligned["ask"] - aligned["exec_price"]), np.maximum(0, aligned["exec_price"] - aligned["bid"]))
        aligned["pi_dollars"] = aligned["pi_per_share"] * aligned["exec_quantity"]
        aligned["slippage"] = (aligned["exec_price"] - aligned["limit_price"]).abs()
        yield aligned

def run_etl() -> None:
    nbbo = load_nbbo()
    orders = load_orders()
    fills_list = []
    for processed_chunk in process_trades_in_chunks(nbbo, orders):
        fills_list.append(processed_chunk)
    fills = pd.concat(fills_list, ignore_index=True)
    fills.sort_values(["exec_timestamp", "symbol"], inplace=True)
    fills.to_csv(OUTPUT_DIR / "fills_normalized.csv", index=False)
    print("Wrote fills_normalized.csv")
    # Order summary
    summary = (
        fills.groupby("order_id")
        .agg(total_order_qty=("quantity", "first"), filled_qty=("exec_quantity", "sum"), vwap=("exec_price", lambda x: np.average(x, weights=fills.loc[x.index, "exec_quantity"])), total_pi_dollars=("pi_dollars", "sum"))
        .reset_index()
    )
    summary["fill_rate"] = summary["filled_qty"] / summary["total_order_qty"]
    summary.to_csv(OUTPUT_DIR / "order_summary.csv", index=False)
    print("Wrote order_summary.csv")

#Helper for FastAPI (/ingest)
"""
Run the existing ETL but with custom CSV locations.
We temporarily swap the module-level paths, call run_etl(), then restore them.
Returns a small dict with output paths and the row counts we wrote.
"""
def run_etl_from_paths(*, orders_path: Path, trades_path: Path, nbbo_path: Path) -> dict:
    global ORDERS_PATH, TRADES_PATH, NBBO_PATH
    old_orders, old_trades, old_nbbo = ORDERS_PATH, TRADES_PATH, NBBO_PATH
    try:
        ORDERS_PATH, TRADES_PATH, NBBO_PATH = orders_path, trades_path, nbbo_path
        run_etl() # run the standard pipeline
        fills_path = OUTPUT_DIR / "fills_normalized.csv"
        summary_path = OUTPUT_DIR / "order_summary.csv"
        #metadata to return to the API caller
        import pandas as pd
        rows = {"fills": len(pd.read_csv(fills_path)) if fills_path.exists() else 0, "summary": len(pd.read_csv(summary_path)) if summary_path.exists() else 0}
        return {"fills_path": fills_path, "summary_path": summary_path, "rows": rows}
    finally: ORDERS_PATH, TRADES_PATH, NBBO_PATH = old_orders, old_trades, old_nbbo

if __name__ == "__main__":
    run_etl()
