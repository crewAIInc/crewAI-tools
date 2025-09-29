from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class BotPersonality(Enum):
    HUNTER = "Hunter"
    EDUCATOR = "Educator"
    CHARMER = "Charmer"
    ANALYTICAL_SDR = "Analytical SDR"
    HUSTLER = "Hustler"
    LISTENER = "Listener"
    INNOVATOR = "Innovator"
    NETWORKER = "Networker"
    CLOSER_IN_TRAINING = "Closer in Training"
    PROCESS_ORIENTED_SDR = "Process-Oriented SDR"

class BotPersona(Enum):
    HUNTER = "Aggressive and persistent, thrives on cold calling and high outbound activity."
    EDUCATOR = "Knowledgeable and consultative, focuses on educating prospects about the product."
    CHARMER = "Personable and engaging, builds rapport effortlessly for social selling."
    ANALYTICAL_SDR = "Data-driven and detail-oriented, personalizes outreach using insights."
    HUSTLER = "Energetic and motivated, excels in high-volume outreach and fast-paced environments."
    LISTENER = "Empathetic and observant, skilled at qualifying leads and uncovering needs."
    INNOVATOR = "Creative and tech-savvy, experiments with new outreach strategies and automation."
    NETWORKER = "Well-connected and social, leverages referrals and relationships for sales."
    CLOSER_IN_TRAINING = "Ambitious and sales-driven, focuses on advancing deals and pushing meetings"
    PROCESS_ORIENTED_SDR = "Structured and disciplined, excels in following sales scripts and methodologies."
class QuestionAnswer(BaseModel):
    """
    A class to represent a question and its answer.
    """
    question: str = Field(..., description="The question")
    answer: str = Field(..., description="The answer")

class Graph8DefaultAgentInfoScrappingGraph(BaseModel):
    company_name: str
    company_description: str
    company_services: List[str]
    company_products: List[str]
    customer_pain_points: List[str]
    outbound_voice_mail_prompt: str
    value_proposition: str
    pitch: str
    faqs: List[QuestionAnswer]
    bot_name: str
    bot_personality: BotPersonality
    persona: BotPersona
    target_audience: str
    competitive_advantage: str
    sales_email: str
    support_email: str
    company_phone: str
    company_website: str
    scraped_url: str
    company_country: str = ""
    company_city: str = ""

from scrapegraph_py import Client

# Initialize the client
client = Client(api_key="sgai-e32215fb-5940-400f-91ea-30af5f35e0c9")

# SmartScraper request
response = client.smartscraper(
    website_url="https://www.jnj.com",
    user_prompt="""
    # Objective
Extract detailed company information based on the provided company data.
# GLOBAL RULES (read first)
1. **Validate before populating.** If the value you extract is invalid, protected, obviously placeholder text (e.g., "info@example.com", "contact@domain.com", "(000) 000-0000", "+1 123 456 7890", "Your Name"), or cannot be confirmed, output an **empty string ""** for that field.
2. **No placeholders of any kind** may appear in the final JSON. Do **not** invent stand-in text like "TBD", "N/A", "Unknown", or "Content not available".
3. Follow normal syntax/formatting for each field:
   • Websites → Valid, reachable URL (http/https).
   • Email addresses → RFC-5322-compliant and company-specific.
   • Phone numbers → Valid E.164 or recognised national format.
   If a value fails validation, set it to "".
4. Base every answer strictly on the provided company information. Logical inference is allowed, but reckless guessing is not.
5. The final output must be **one JSON object** with the keys listed below, in the exact order shown. Every value must be a string (including "" when empty).
# FIELDS TO EXTRACT
- **company_name** – Full legal or trading name of the company.
- **company_description** – 2–3 sentences on mission, industry, and what they do.
- **company_services** – Three distinct services (comma-separated).
- **company_country** – Country where the company is headquartered.
- **company_city** – City where the company is headquartered.
- **company_products** – Three main products (comma-separated).
- **customer_pain_points** – Key customer challenges the company addresses.
- **outbound_voice_mail_prompt** – Friendly, concise voicemail script (no fillers or placeholders).
- **value_proposition** – What differentiates the company and the value it delivers.
- **pitch** – 2–3 sentence outbound sales pitch.
- **faq** – ≥3 FAQ Q&A pairs separated by line breaks, e.g.,
  `Q: …\nA: …`
- **bot_name** – Suitable name for the company’s bot.
- **bot_personality** – ONE personality descriptor (e.g., "Helpful", "Upbeat").
- **persona** – ONE concise persona label (e.g., "Sales Assistant").
- **target_audience** – Primary audience segments.
- **competitive_advantage** – Main competitive edge.
- **sales_email** – Valid sales/BD email; else "".
- **support_email** – Valid support email; else "".
- **company_phone** – Valid phone number; else "".
- **company_website** – Official accessible website URL; else "".
- **scrapped_url** – Source URL for the data; else "".
# OUTPUT FORMAT
Return **only** the JSON object—no commentary, no markdown—matching this structure:
```json
{{
  "company_name": "",
  "company_description": "",
  "company_services": "",
  "company_country": "",
  "company_city": "",
  "company_products": "",
  "customer_pain_points": "",
  "outbound_voice_mail_prompt": "",
  "value_proposition": "",
  "pitch": "",
  "faq": "",
  "bot_name": "",
  "bot_personality": "",
  "persona": "",
  "target_audience": "",
  "competitive_advantage": "",
  "sales_email": "",
  "support_email": "",
  "company_phone": "",
  "company_website": "",
  "scrapped_url": ""
}}
```
# PROCESS STEPS (internal, not output)
1. Parse the provided company data.
2. Validate each candidate email, phone number, and URL.
   • If it matches placeholder patterns or fails validation, set value to "".
3. Populate every key according to the rules above.
4. Output the JSON object and nothing else.
"""
)

print("Result:", response)