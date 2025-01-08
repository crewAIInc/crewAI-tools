import os

from .crm_tool import CrmBaseTool, CrmType
from .hubspot_tool import HubSpotTool
from .salesforce_tool import SalesforceTool


class CrmToolFactory:
    @staticmethod
    def create_crm_tool(crm_type: CrmType) -> CrmBaseTool:
        base_url = os.getenv(f"{crm_type}_BASE_URL")
        api_key = os.getenv(f"{crm_type}_API_KEY")

        if not base_url or not api_key:
            raise ValueError(f"Environment variables for {crm_type} are not set.")

        if crm_type == CrmType.SALESFORCE:
            client_id = os.getenv("SALESFORCE_CLIENT_ID")
            client_secret = os.getenv("SALESFORCE_CLIENT_SECRET")
            refresh_token = os.getenv("SALESFORCE_REFRESH_TOKEN")
            if not client_id or not client_secret or not refresh_token:
                raise ValueError("Salesforce OAuth credentials are not set.")
            return SalesforceTool(
                base_url, api_key, client_id, client_secret, refresh_token
            )
        elif crm_type == CrmType.HUBSPOT:
            return HubSpotTool(base_url, api_key)
        else:
            raise ValueError(f"Unsupported CRM tool: {crm_type}")
