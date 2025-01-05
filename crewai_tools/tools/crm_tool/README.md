# CRM Tools

## Description
The CRM Tools are designed for seamless interaction with popular CRM platforms like Salesforce and HubSpot. 
These tools allow you to integrate with CRM systems, perform data operations, 
and automate tasks such as lead management, email campaigns, and more.

Currently, the following CRM platforms are supported:

- **Salesforce**
- **HubSpot**

To successfully use these tools, you need to have the appropriate API keys and credentials set in your environment.

## Installation
To start using the CRM Integration Tools, you must first install the `crewai_tools` package. 
This can be easily done with the following command:


```shell
pip install 'crewai[tools]'
```

## Setup
Before you begin, ensure you have set the required environment variables for both Salesforce and HubSpot.

### Environment Variables
You need to set the following environment variables:

- **For Salesforce:**
  - `SALESFORCE_API_KEY`: Your Salesforce API key
  - `SALESFORCE_BASE_URL`: Base URL for Salesforce API
  - `SALESFORCE_CLIENT_ID`: Salesforce Client ID
  - `SALESFORCE_CLIENT_SECRET`: Salesforce Client Secret
  - `SALESFORCE_REFRESH_TOKEN`: Salesforce refresh token

- **For HubSpot:**
  - `HUBSPOT_API_KEY`: Your HubSpot API key
  - `HUBSPOT_BASE_URL`: Base URL for HubSpot API

You can set these environment variables using the terminal or by including them in a `.env` file.

### Example of `.env` file:
```
SALESFORCE_API_KEY=your_salesforce_api_key
SALESFORCE_BASE_URL=https://api.salesforce.com
SALESFORCE_CLIENT_ID=your_salesforce_client_id
SALESFORCE_CLIENT_SECRET=your_salesforce_client_secret
SALESFORCE_REFRESH_TOKEN=your_salesforce_refresh_token

HUBSPOT_API_KEY=your_hubspot_api_key
HUBSPOT_BASE_URL=https://api.hubspot.com
```

## Examples

### Creating Salesforce Tool Using Factory
Here is how you can use the `CrmToolFactory` to create a Salesforce integration tool and fetch data from Salesforce:

```python
from crewai_tools.tools import CrmDataType, CrmToolFactory, CrmType

# Create Salesforce tool instance using the factory
sf = CrmToolFactory.create_crm_tool(CrmType.SALESFORCE)

# Fetch Salesforce data (e.g., contacts)
contacts = sf.fetch_data(CrmDataType.CONTACTS)
print(contacts)
```

### Creating HubSpot Tool Using Factory
Similarly, you can create a HubSpot tool instance using the factory and fetch data from HubSpot:

```python
from crewai_tools.tools import CrmDataType, CrmToolFactory, CrmType

# Create HubSpot tool instance using the factory
hs = CrmToolFactory.create_crm_tool(CrmType.HUBSPOT)

# Fetch HubSpot data (e.g., contacts)
contacts = hs.fetch_data(CrmDataType.CONTACTS)
print(contacts)
```

## Features

### Automated Lead Management:
- **Lead Scoring**: Automatically assess and rank leads based on predefined criteria.
- **Lead Assignment**: Distribute leads to appropriate sales representatives based on territory, expertise, or workload.

### Personalized Customer Interactions:
- **Email Campaigns**: Craft and dispatch personalized emails to prospects and customers.
- **Follow-Up Scheduling**: Set reminders and schedule follow-ups for maintaining consistent communication.

### Data Enrichment and Maintenance:
- **Information Update**: Enrich CRM records by fetching additional data from external sources.
- **Data Cleansing**: Identify and rectify inconsistencies or duplicates in CRM data.

### Sales Pipeline Optimization:
- **Opportunity Tracking**: Monitor the progression of deals and alert for stalled opportunities.
- **Forecasting**: Analyze historical data to predict future sales trends.

### Customer Support Enhancement:
- **Ticket Routing**: Automatically assign support tickets to the most suitable agents.
- **Response Generation**: Generate initial responses to customer inquiries.

### Marketing Automation:
- **Campaign Management**: Plan, execute, and monitor marketing campaigns directly from CRM.
- **Content Recommendations**: Suggest relevant content based on customer behavior.

### Analytics and Reporting:
- **Performance Dashboards**: Generate real-time dashboards displaying key metrics.
- **Custom Reports**: Create tailored reports for analyzing specific aspects of business processes.


