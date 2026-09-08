import mysql.connector
from mysql.connector import Error
import numpy as np
import pandas as pd
from tabulate import tabulate

# ---------------------------------------------------------
# 1. Read Data from Excel
# ---------------------------------------------------------
excel_path = "new-employees.xlsx"

# Read the first sheet (or specify sheet_name='Sheet1')
df = pd.read_excel(excel_path)

print(tabulate(df, headers="keys", tablefmt="fancy_grid"))

# ---------------------------------------------------------
# 2. Clean and Transform Data
# ---------------------------------------------------------
# Standardize column headers (lowercase, trim whitespace, replace spaces)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Strip surrounding whitespace from string columns
string_cols = ["full_name", "email_address"]
for col in string_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Clean email: lowercase and drop rows without valid email addresses
if "email_address" in df.columns:
    df["email_address"] = df["email_address"].str.lower()
    # Replace strings that became "nan" from empty cells
    df["email_address"] = df["email_address"].replace("nan", np.nan)

# Clean salary: remove symbols, convert to numeric, fill nulls with default or drop
if "salary" in df.columns:
    df["salary"] = (
        df["salary"].astype(str).str.replace(r"[$,]", "", regex=True)
    )
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

# Clean hire_date: standardize to YYYY-MM-DD
if "hire_date" in df.columns:
    df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce").dt.date

# Handle missing or duplicate data
# Check for critical columns before attempting to drop rows or duplicates
critical_cols = ["full_name", "email"]
existing_critical_cols = [col for col in critical_cols if col in df.columns]

if existing_critical_cols:
    df = df.dropna(subset=existing_critical_cols)  # Drop rows missing critical keys

if "email_address" in df.columns:
    df = df.drop_duplicates(subset=["email_address"])  # Prevent unique constraint errors

# Replace any lingering pandas/numpy NaN with Python None (converts to SQL NULL)
cleaned_df = df.replace({np.nan: None})

# Convert records to a list of tuples for parameterized insertion
# Use .get() to avoid KeyError if a column is missing from the DataFrame
expected_db_cols = ["full_name", "email_address", "salary", "hire_date"]
records_to_insert = [
    tuple(row.get(col) for col in expected_db_cols)
    for _, row in cleaned_df.iterrows()
]

# ---------------------------------------------------------
# 3. Insert into MySQL Database
# ---------------------------------------------------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "BeachView2025@",
    "database": "lind_pair_programming",
    "auth_plugin": "mysql_native_password",
    "port": 3306,
}

insert_query = """
    insert into new_employees (name, email, salary, hire_date)
    values (%s, %s, %s, %s)
    on duplicate key update
        salary = values(salary),
        hire_date = values(hire_date);
"""

connection = None
cursor = None

try:
    connection = mysql.connector.connect(**db_config)

    if connection.is_connected():
        cursor = connection.cursor()

        # Batch execution
        cursor.executemany(insert_query, records_to_insert)
        connection.commit()

        print(f"Successfully processed {cursor.rowcount} rows into MySQL.")

except Error as err:
    if connection:
        connection.rollback()
    print(f"Database error: {err}")

finally:
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()