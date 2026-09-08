import sqlite3
import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


# ==========================================
# 1. EXTRACT: Ingest raw data from source
# ==========================================
def extract_raw_orders() -> pd.DataFrame:
    """Simulates ingesting raw customer purchase events from an API or CSV."""
    raw_data = {
        "order_id": [101, 102, 103, 104, 105, 106],
        "customer_id": ["C1", "C2", "C1", "C3", "C2", None],
        "amount": ["$120.50", "$45.00", "$300.00", "invalid", "$75.25", "$50.00"],
        "order_date": [
            "2026-03-01 10:30:00",
            "2026-03-01 11:15:00",
            "2026-03-02 09:00:00",
            "2026-03-02 14:20:00",
            "2026-03-03 16:45:00",
            "2026-03-03 18:00:00",
        ],
        "status": ["completed", "completed", "refunded", "completed", "completed", "pending"]
    }
    return pd.DataFrame(raw_data)


# ==========================================
# 2. TRANSFORM: Clean, validate, and enrich
# ==========================================
def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans currency strings, filters invalid rows, and enriches data."""
    # Drop rows missing critical identifiers
    clean_df = df.dropna(subset=["customer_id"]).copy()

    # Clean amount column and cast to numeric
    clean_df["amount"] = (
        clean_df["amount"]
        .astype(str)
        .str.replace("$", "", regex=False)
    )
    clean_df["amount"] = pd.to_numeric(clean_df["amount"], errors="coerce")
    clean_df = clean_df.dropna(subset=["amount"])

    # Parse timestamps and extract calendar date
    clean_df["order_timestamp"] = pd.to_datetime(clean_df["order_date"])
    clean_df["order_date"] = clean_df["order_timestamp"].dt.date

    # Enrich: add processing metadata
    clean_df["processed_at"] = datetime.utcnow().isoformat()

    # Keep only successful orders
    filtered_df = clean_df[clean_df["status"] == "completed"]

    return filtered_df[["order_id", "customer_id", "amount", "order_date", "processed_at"]]


# ==========================================
# 3. LOAD: Persist transformed data to DB
# ==========================================
def load_to_warehouse(df: pd.DataFrame, db_path: str = "analytics.db") -> None:
    """Appends records into an analytical SQLite database."""
    with sqlite3.connect(db_path) as conn:
        df.to_sql("fact_orders", conn, if_exists="append", index=False)
        print(f"Loaded {len(df)} records into 'fact_orders'.")


# ==========================================
# 4. ORCHESTRATE: Run pipeline workflow
# ==========================================
def run_pipeline():
    print("[Pipeline] Starting run...")

    # Extract
    raw_df = extract_raw_orders()
    print(f"[Extract] Retrieved {len(raw_df)} raw records.")

    # Transform
    processed_df = transform_orders(raw_df)
    print(f"[Transform] Cleaned down to {len(processed_df)} valid records.")

    # Load
    load_to_warehouse(processed_df)
    print("[Pipeline] Run finished successfully.")


if __name__ == "__main__":
    run_pipeline()