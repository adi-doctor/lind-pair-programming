from datetime import datetime
from pathlib import Path
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# Define paths
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

CSV_FILE = DATA_DIR / "raw_transactions.csv"
EXCEL_FILE = DATA_DIR / "customer_directory.xlsx"
OUTPUT_FILE = DATA_DIR / "processed_orders.csv"


# ==========================================
# 0. SETUP: Create Sample Source Files
# ==========================================
def generate_sample_files():
    """Generates the raw CSV and Excel files for demonstration."""
    raw_csv_data = """transaction_id,customer_id,raw_amount,status,transaction_time
TX101,C101,$125.50,completed,2026-03-01 09:15:00
TX102,C102,$45.00,completed,2026-03-01 10:45:00
TX103,C103,bad_data,completed,2026-03-02 11:20:00
TX104,C101,$310.00,refunded,2026-03-02 14:00:00
TX105,C999,$89.99,completed,2026-03-03 16:30:00
TX106,,$15.00,completed,2026-03-03 18:00:00
"""
    with open(CSV_FILE, "w") as f:
        f.write(raw_csv_data.strip())

    excel_data = {
        "customer_id": ["C101", "C102", "C103"],
        "customer_name": ["Alice Smith", "Bob Jones", "Charlie Brown"],
        "region": ["North America", "Europe", "Asia-Pacific"],
    }
    pd.DataFrame(excel_data).to_excel(EXCEL_FILE, sheet_name="Customers", index=False)


# ==========================================
# 1. EXTRACT: Read from CSV & Excel
# ==========================================
def extract_sources(csv_path: Path, excel_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reads transactional data from CSV and customer dimensions from Excel."""
    print("[Extract] Ingesting CSV and Excel files...")

    # Read CSV
    transactions_df = pd.read_csv(csv_path)

    # Read specific sheet from Excel using the openpyxl engine
    customers_df = pd.read_excel(excel_path, sheet_name="Customers", engine="openpyxl")

    return transactions_df, customers_df


# ==========================================
# 2. TRANSFORM: Clean, Convert, and Join
# ==========================================
def transform_data(transactions_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans numeric currency strings, joins files, and adds metadata."""
    print("[Transform] Cleaning and joining datasets...")

    # Drop missing critical keys
    df = transactions_df.dropna(subset=["customer_id"]).copy()

    # Clean currency string to float: remove '$' and coerce bad strings to NaN
    df["clean_amount"] = (
        df["raw_amount"]
        .astype(str)
        .str.replace("$", "", regex=False)
    )
    df["clean_amount"] = pd.to_numeric(df["clean_amount"], errors="coerce")
    df = df.dropna(subset=["clean_amount"])

    # Parse timestamps
    df["transaction_time"] = pd.to_datetime(df["transaction_time"])
    df["date"] = df["transaction_time"].dt.date

    # Filter only completed transactions
    df = df[df["status"] == "completed"]

    # Join with customer dimension from Excel (Inner Join drops non-existent customer IDs)
    merged_df = pd.merge(df, customers_df, on="customer_id", how="inner")

    # Select and order final fields
    final_df = merged_df[[
        "transaction_id",
        "customer_id",
        "customer_name",
        "region",
        "clean_amount",
        "date"
    ]].copy()

    # Add pipeline metadata
    final_df["processed_at"] = datetime.utcnow().isoformat()

    return final_df


# ==========================================
# 3. LOAD: Persist to Target File
# ==========================================
def load_to_file(df: pd.DataFrame, target_path: Path) -> None:
    """Exports processed data into a clean CSV format."""
    print(f"[Load] Writing {len(df)} records to {target_path}...")
    df.to_csv(target_path, index=False)


# ==========================================
# 4. ORCHESTRATE: Pipeline Execution
# ==========================================
def run_pipeline():
    # Generate mock files if running standalone
    generate_sample_files()

    # Step 1: Extract
    raw_tx, raw_customers = extract_sources(CSV_FILE, EXCEL_FILE)

    # Step 2: Transform
    cleaned_df = transform_data(raw_tx, raw_customers)

    # Step 3: Load
    load_to_file(cleaned_df, OUTPUT_FILE)
    print("[Pipeline] Execution complete.")


if __name__ == "__main__":
    run_pipeline()