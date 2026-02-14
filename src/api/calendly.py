"""Calendly API wrapper"""
import os
from typing import Any

import requests


class CalendlyAPIError(Exception):
    pass


class CalendlyClient:
    """
    Generated and then edited wrapper around Calendly v2 API.
    https://developer.calendly.com/api-docs
    """

    def __init__(self, api_token: str | None = None):
        self.api_token = api_token or os.getenv("CALENDLY_API_TOKEN")
        if not self.api_token:
            raise ValueError("Calendly API token must be provided or set in CALENDLY_API_TOKEN")

        self.base_url = "https://api.calendly.com"

    # Helpers

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = requests.get(url, headers=self._headers(), params=params, timeout=20)
        if not response.ok:
            raise CalendlyAPIError(f"GET {url} failed: {response.status_code} {response.text}")
        return response.json()

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = requests.post(url, headers=self._headers(), json=payload, timeout=20)
        if not response.ok:
            raise CalendlyAPIError(f"POST {url} failed: {response.status_code} {response.text}")
        return response.json()

    # Endpoints

    def get_current_user(self) -> dict[str, Any]:
        return self._get("/users/me")

    def list_event_types(self, organization: str | None = None, user: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if organization:
            params["organization"] = organization
        if user:
            params["user"] = user
        data = self._get("/event_types", params=params)
        return data.get("collection", [])

    def list_scheduled_events(
        self,
        user: str | None = None,
        organization: str | None = None,
        count: int = 20,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"count": count}
        if user:
            params["user"] = user
        if organization:
            params["organization"] = organization
        if status:
            params["status"] = status

        data = self._get("/scheduled_events", params=params)
        return data.get("collection", [])

    def list_event_invitees(self, event_uri: str) -> list[dict[str, Any]]:
        params = {"event": event_uri}
        data = self._get("/scheduled_events/{}/invitees".format(event_uri.split("/")[-1]), params=params)
        return data.get("collection", [])

    def create_invitee_no_show(self, invitee_uri: str) -> dict[str, Any]:
        payload = {"invitee": invitee_uri}
        return self._post("/invitee_no_shows", payload)

    def list_event_type_available_times(
        self,
        event_type: str,
        start_time: str,
        end_time: str,
        timezone: str | None = None,
        **extra_params: Any,
    ) -> list[dict[str, Any]]:
        if "/" not in event_type:
            event_type_uri = f"{self.base_url}/event_types/{event_type}"
        else:
            event_type_uri = event_type

        params: dict[str, Any] = {
            "event_type": event_type_uri,
            "start_time": start_time,
            "end_time": end_time,
        }

        if timezone:
            params["timezone"] = timezone

        params.update(extra_params)

        data = self._get("/event_type_available_times", params=params)
        return data.get("collection", [])

    def create_invitee(
        self,
        event_type: str,
        start_time: str,
        invitee: dict[str, Any],
        location: dict[str, Any],
    ) -> dict[str, Any]:
        if "/" not in event_type:
            event_type_uri = f"{self.base_url}/event_types/{event_type}"
        else:
            event_type_uri = event_type

        payload = {
            "event_type": event_type_uri,
            "start_time": start_time,
            "invitee": invitee,
            "location": location,
        }
        return self._post("/invitees", payload)

    def cancel_event(
        self,
        event_uuid: str,
    ) -> dict[str, Any]:
        payload = {
            # TODO: "reason": reason,
        }
        return self._post(f"/scheduled_events/{event_uuid}/cancellation", payload)
