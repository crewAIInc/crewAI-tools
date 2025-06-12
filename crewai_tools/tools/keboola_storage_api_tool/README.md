# Keboola Storage API Tool

The Keboola Storage API Tool is a set of CrewAI-compatible extensions built to connect Keboola’s Storage API with 
intelligent agents. 

This suite empowers CrewAI workflows to programmatically interact with Keboola’s structured data platform across 
all supported cloud providers:

- ✅ Table extraction (this tool)
- ⬜ Table upload (planned)
- ⬜ Bucket/table metadata listing (planned)

This toolset is cloud-aware — designed to support federated authentication and export flows across AWS, GCP, and Azure-based Keboola stacks.

## Table extraction Tool (KeboolaTableExtractTool)

This is the first tool in the Keboola Storage API suite. It enables CrewAI agents to export and read tables from Keboola via the [async export API](https://keboola.docs.apiary.io/#reference/tables/unload-data-asynchronously).

### Features

- Works with all Keboola stacks, including:

  - https://connection.keboola.com (AWS US East 1)
  - https://connection.eu-central-1.keboola.com (AWS EU Central 1)
  - https://connection.north-europe.azure.keboola.com (Azure)
  - https://connection.europe-west3.gcp.keboola.com (GCP EU)
  - https://connection.us-east4.gcp.keboola.com (GCP US)

- Automatically detects the backend (`gs://`, `s3://`, or `azure://`).
- Downloads and merges slices into a single CSV string.
- CrewAI-compatible with structured input validation.

## Installation

Install `crewai-tools` along with required dependencies:

```bash
pip install 'crewai[tools]' pandas requests boto3 google-auth
```

### Configuration

You must pass the following arguments when using the tool:

| Param       | Description                                     |
| ----------- | ----------------------------------------------- |
| `api_token` | A Keboola Storage API token with read access    |
| `table_id`  | Full table ID (e.g., `in.c-bucket.my_table`)    |
| `base_url`  | URL of the Keboola stack (see supported stacks) |

### Usage Example (Manual)

```python
from keboola_storage_api_tool.keboola_table_extract_tool import KeboolaTableExtractTool

tool = KeboolaTableExtractTool()

csv = tool.run({
    "table_id": "in.c-my-bucket.sales_data",
    "api_token": "your_keboola_token",
    "base_url": "https://connection.eu-central-1.keboola.com"
})

print(csv[:500])  # preview first 500 characters
```

### Usage in a CrewAI Agent

```python
from crewai import Agent, Task, Crew
from keboola_storage_api_tool.keboola_table_extract_tool import KeboolaTableExtractTool

extract_tool = KeboolaTableExtractTool()

agent = Agent(
    role="Data Downloader",
    goal="Extract and preview usage data from Keboola",
    backstory="You're a data analyst that pulls structured records from Keboola tables.",
    tools=[extract_tool],
    verbose=True
)

task = Task(
    description="Use the tool to fetch a CSV export of the 'in.c-usage.usage_data' table.",
    expected_output="First 5 rows of the exported CSV",
    agent=agent,
    async_execution=False,
    arguments={
        "table_id": "in.c-usage.usage_data",
        "api_token": "your_token",
        "base_url": "https://connection.eu-central-1.keboola.com"
    }
)

crew = Crew(agents=[agent], tasks=[task])
crew.kickoff()
```

### Returns

Returns the full table content as a **CSV string**, ready for parsing or downstream analysis.

### Error Handling

- `ValueError`: if credentials or arguments are missing
- `TimeoutError`: if the async export job does not finish
- `requests.exceptions.HTTPError`: for Keboola API or GCP/AWS/Azure download issues

### Resources

- [Keboola Storage API Docs](https://keboola.docs.apiary.io)
- [CrewAI Documentation](https://docs.crewai.com)

> 🛠️ Built and maintained by [Keboola](https://www.keboola.com) as an official CrewAI tool extension for the Keboola platform.