from abc import ABC, abstractmethod
from enum import Enum

import requests
from crewai.tools import BaseTool


class CrmType(Enum):
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"


# Enum for data types
class CrmDataType(Enum):
    LEADS = "leads"
    CONTACTS = "contacts"
    OPPORTUNITIES = "opportunities"
    DEALS = "deals"


class CrmBaseTool(BaseTool, ABC):
    def __init__(self, base_url, api_key, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.api_key = api_key

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data=None,
        params=None,
        retry_on_auth_failure=True,
    ):
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.request(
                method, url, headers=headers, json=data, params=params
            )
            if response.status_code == 401 and retry_on_auth_failure:
                print("Token expired. Refreshing token...")
                self._refresh_token()
                return self._make_request(
                    method, endpoint, data, params, retry_on_auth_failure=False
                )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"HTTP request failed: {e}")

    def _refresh_token(self):
        raise NotImplementedError("Token refresh is not implemented for this CRM.")

    def get(self, endpoint, params=None):
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._make_request("POST", endpoint, data=data)

    def put(self, endpoint, data=None):
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint):
        return self._make_request("DELETE", endpoint)

    @abstractmethod
    def fetch_crm_data(self, data_type: CrmDataType):
        """Fetch data from the CRM system based on the type of data requested."""

    @abstractmethod
    def lead_scoring(self, criteria: dict):
        """Assess and rank leads."""

    @abstractmethod
    def send_email(self, subject: str, body: str, recipients: list):
        """Send an email campaign."""

    @abstractmethod
    def track_opportunities(self):
        """Monitor sales pipeline opportunities."""
