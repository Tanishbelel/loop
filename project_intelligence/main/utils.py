import os
import time
import jwt
import requests
from threading import Lock
from dotenv import load_dotenv

load_dotenv()


class GithubUtils:
    """
    Utility class for GitHub App authentication
    """

    _token_cache = {}
    _lock = Lock()

    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        pem_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")

        with open(pem_path, "r") as f:
            self.private_key = f.read()

        if not self.app_id or not self.private_key:
            raise Exception("Missing GitHub App environment variables")

        self.private_key = self.private_key.replace("\\n", "\n")

    # ------------------------------
    # Generate JWT
    # ------------------------------
    def _generate_jwt(self):
        now = int(time.time())

        payload = {
            "iat": now - 60,  # allow small clock drift
            "exp": now + 540,  # must be <= 10 min
            "iss": self.app_id
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256")

    # ------------------------------
    # Get Installation Token
    # ------------------------------
    def get_installation_token(self, installation_id: str):

        with self._lock:
            cached = self._token_cache.get(installation_id)

            if cached and cached["expires_at"] > time.time():
                return cached["token"]

            jwt_token = self._generate_jwt()

            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json"
            }

            url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

            response = requests.post(url, headers=headers)

            if response.status_code != 201:
                raise Exception(f"GitHub token error: {response.text}")

            data = response.json()

            token = data["token"]
            expires_at = time.time() + 3500  # ~1 hour minus buffer

            self._token_cache[installation_id] = {
                "token": token,
                "expires_at": expires_at
            }

            return token
