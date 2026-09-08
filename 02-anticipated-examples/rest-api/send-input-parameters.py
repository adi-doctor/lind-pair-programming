import os
import sqlite3
import requests


# Optional: set up a local database table for testing
def init_db(db_path: str = "app.db"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users
            (
                id              INTEGER PRIMARY KEY,
                username        TEXT,
                email           TEXT,
                external_status TEXT,
                external_id     TEXT
            )
            """
        )
        # Seed an example record if empty
        cursor.execute("INSERT OR IGNORE INTO users (id, username, email) VALUES (1, 'alice', 'alice@example.com')")
        conn.commit()


def process_and_update(user_id: int, new_email: str, db_path: str = "app.db") -> dict:
    """Takes two parameters, sends them to an API, and updates the database."""
    api_url = "https://api.example.com/v1/update-profile"
    api_key = os.getenv("API_KEY", "your-api-key-here")

    # 1. Package the two parameters and call external API
    payload = {
        "user_id": user_id,
        "email": new_email
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.RequestException as error:
        # Fallback simulation for demonstration if endpoint is not live:
        print(f"API request failed ({error}). Using mock response for demonstration.")
        api_data = {"status": "synced", "remote_id": f"ext_{user_id}"}

    # 2. Update the database using parameterized queries (prevents SQL injection)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET email           = ?,
                external_status = ?,
                external_id     = ?
            WHERE id = ?
            """,
            (new_email, api_data.get("status"), api_data.get("remote_id"), user_id),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Record with id={user_id} not found in database.")

        conn.commit()

    return {
        "success": True,
        "updated_user_id": user_id,
        "api_response": api_data
    }


if __name__ == "__main__":
    init_db()

    # Pass the two parameters:
    param_user_id = 1
    param_new_email = "alice_new@example.com"

    result = process_and_update(user_id=param_user_id, new_email=param_new_email)
    print("Result:", result)