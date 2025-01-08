from .crm_tool import CrmBaseTool, CrmDataType


class HubSpotTool(CrmBaseTool):
    def fetch_crm_data(self, data_type: CrmDataType):
        if data_type == CrmDataType.CONTACTS:
            return self.get("contacts")
        elif data_type == CrmDataType.DEALS:
            return self.get("deals/v1/deal")
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    def lead_scoring(self, criteria: dict):
        contacts = self.get("contacts")
        scored_contacts = []
        for contact in contacts.get("results", []):
            score = sum(
                contact.get(key, 0) * weight for key, weight in criteria.items()
            )
            scored_contacts.append({"contact": contact, "score": score})
        return scored_contacts

    def send_email(self, subject: str, body: str, recipients: list):
        email_data = {
            "subject": subject,
            "html": body,
            "recipients": [{"email": email} for email in recipients],
        }
        return self.post("email/public/v1/send", data=email_data)

    def track_opportunities(self):
        return self.get("deals/v1/deal")
