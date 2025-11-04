from pathlib import Path
import os

import pandas as pd
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OUTPUT_DIR = Path("output")
DB_NAME = os.getenv("MONGO_DB")
MONGO_URI = os.getenv("MONGO_URI")


def load_csv_to_mongo(df: pd.DataFrame, collection, key_fields: list[str]):
    """
    Clears and loads a DataFrame into a MongoDB collection.
    Idempotent: replaces existing documents with the same key(s).
    """
    # Convert NaN to None for Mongo
    records = df.replace({pd.NA: None}).to_dict(orient="records")

    # Build a compound filter for upserts
    for rec in records:
        query = {k: rec[k] for k in key_fields if k in rec}
        collection.replace_one(query, rec, upsert=True)


def create_indexes(db):
    """
    Create indexes for the orders and trades collections.
    """
    db.trades.create_index([("order_id", ASCENDING)])
    db.trades.create_index([("symbol", ASCENDING)])
    db.trades.create_index([("exec_timestamp", ASCENDING)])
    db.orders.create_index([("order_id", ASCENDING)], unique=True)


def run_load():
    """
    Load ETL output CSVs into MongoDB, create indexes, and print top orders.
    """
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    fills_path = OUTPUT_DIR / "fills_normalized.csv"
    orders_path = OUTPUT_DIR / "order_summary.csv"

    if not fills_path.exists() or not orders_path.exists():
        raise FileNotFoundError("Expected ETL outputs not found under /output")

    # Load CSVs
    trades_df = pd.read_csv(fills_path)
    orders_df = pd.read_csv(orders_path)

    # Load to MongoDB
    print("Loading trades...")
    load_csv_to_mongo(trades_df, db.trades, key_fields=["trade_id"])

    print("Loading orders...")
    load_csv_to_mongo(orders_df, db.orders, key_fields=["order_id"])

    # Create indexes
    print("Creating indexes...")
    create_indexes(db)

    # Example query — Top 5 orders by total_pi_dollars
    top_orders = list(
        db.orders.find({}, {"_id": 0})
        .sort("total_pi_dollars", -1)
        .limit(5)
    )

    print("\nTop 5 orders by total_pi_dollars:")
    for order in top_orders:
        print(order)

    print("Load complete.")
    client.close()


if __name__ == "__main__":
    run_load()
