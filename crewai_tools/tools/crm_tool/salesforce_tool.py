import requests
from crm_tool import CrmBaseTool, CrmDataType


class SalesforceTool(CrmBaseTool):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        **kwargs,
    ):
        super().__init__(base_url, api_key, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

    def _refresh_token(self):
        url = f"{self.base_url}/services/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        self.api_key = response.json().get("access_token")

    def fetch_crm_data(self, data_type: CrmDataType):
        if data_type == CrmDataType.LEADS:
            return self.get("sobjects/Lead")
        elif data_type == CrmDataType.CONTACTS:
            return self.get("sobjects/Contact")
        elif data_type == CrmDataType.OPPORTUNITIES:
            return self.get("sobjects/Opportunity")
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    def lead_scoring(self, criteria: dict):
        leads = self.get("sobjects/Lead")
        scored_leads = []
        for lead in leads.get("records", []):
            score = sum(lead.get(key, 0) * weight for key, weight in criteria.items())
            scored_leads.append({"lead": lead, "score": score})
        return scored_leads

    def send_email(self, subject: str, body: str, recipients: list):
        email_data = {
            "Subject": subject,
            "HtmlBody": body,
            "ToAddress": ",".join(recipients),
        }
        return self.post("sobjects/EmailMessage", data=email_data)

    def track_opportunities(self):
        return self.get("sobjects/Opportunity")
