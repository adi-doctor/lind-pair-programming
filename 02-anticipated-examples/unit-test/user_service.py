import requests


class UserService:
    BASE_URL = "https://api.example.com"

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def get_user_email(self, user_id: int) -> str:
        """Fetch user data and return the user's email."""
        url = f"{self.BASE_URL}/users/{user_id}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data["email"]
        except requests.exceptions.HTTPError as exc:
            if response.status_code == 404:
                raise ValueError(f"User {user_id} not found") from exc
            raise RuntimeError(f"API returned error: {response.status_code}") from exc
        except requests.exceptions.RequestException as exc:
            raise ConnectionError("Network failure connecting to User API") from exc