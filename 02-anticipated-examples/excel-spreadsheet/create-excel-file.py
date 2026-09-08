import pandas as pd

# Sample data containing typical real-world inconsistencies:
# - Mixed case and whitespace in column names
# - Currency symbols and commas in salary
# - Extra spaces in strings
# - Mixed date formats
# - A duplicate email and a missing critical field
raw_data = {
    " Full Name ": [
        "  Alice Smith ",
        "Bob Jones",
        "Charlie Brown",
        "Diana Prince",
        "Evan Wright",
        "  Frank Miller",
    ],
    "Email Address": [
        "alice.smith@example.com ",
        "BOB.JONES@EXAMPLE.COM",
        "charlie.brown@example.com",
        "alice.smith@example.com",  # Duplicate email
        None,                       # Missing email
        "frank.m@example.com",
    ],
    " Salary ": [
        "$85,000",
        " 62000 ",
        "$105,500.50",
        "$92,000",
        "$74,000",
        "N/A",                      # Non-numeric value
    ],
    "Hire Date": [
        "2021-03-15",
        "06/20/2019",
        "2018/11/05",
        "2022-01-10",
        "2020-08-25",
        "2023-04-01",
    ],
}

df = pd.DataFrame(raw_data)

# Export to Excel
file_path = "new-employees.xlsx"
df.to_excel(file_path, index=False, engine="openpyxl")

print(f"File created successfully: {file_path}")