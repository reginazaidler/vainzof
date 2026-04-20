from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GSC_ENDPOINT_TEMPLATE = "https://www.googleapis.com/webmasters/v3/sites/{site_url}/searchAnalytics/query"


@dataclass
class GSCClient:
    client_id: str
    client_secret: str
    refresh_token: str
    site_url: str
    timeout: int = 20

    def _get_access_token(self) -> str:
        token_url = TOKEN_ENDPOINT
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(
            token_url,
            data=payload,
            timeout=30,
        )

        if not response.ok:
            print("Token response status:", response.status_code)
            print("Token response body:", response.text)
            self._raise_token_error(response)

        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise RuntimeError("Failed to obtain Google OAuth access token")
        return token

    @staticmethod
    def _raise_token_error(response: requests.Response) -> None:
        try:
            payload = response.json()
        except ValueError:
            response.raise_for_status()
            return

        error = payload.get("error")
        description = payload.get("error_description", "")
        if response.status_code == 400 and error == "invalid_grant":
            guidance = (
                "Google OAuth refresh token is invalid (expired, revoked, or issued in Testing mode). "
                "Generate a new refresh token and update GSC_REFRESH_TOKEN. "
                "If this token keeps expiring after 7 days, publish the OAuth consent screen to Production "
                "before generating a new token."
            )
            raise RuntimeError(f"{guidance} Google said: {description or 'invalid_grant'}") from None

        response.raise_for_status()

    def query_search_analytics(
        self,
        start_date: str,
        end_date: str,
        row_limit: int,
        start_row: int,
    ) -> list[dict[str, Any]]:
        token = self._get_access_token()
        endpoint = GSC_ENDPOINT_TEMPLATE.format(site_url=requests.utils.quote(self.site_url, safe=""))

        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query", "page"],
            "rowLimit": row_limit,
            "startRow": start_row,
        }

        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        rows = response.json().get("rows", [])
        return rows
