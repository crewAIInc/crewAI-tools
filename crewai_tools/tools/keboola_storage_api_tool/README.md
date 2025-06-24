# Keboola Storage API Tool

The Keboola Storage API Tool is a set of [CrewAI](https://www.crewai.com)-compatible tools that empower agents to interact with structured data from the 
[Keboola](https://www.keboola.com) platform across all major cloud providers.

This suite supports:

- [x] Table extraction (`KeboolaTableExtractTool`)
- [ ] Table upload (coming soon)
- [ ] Bucket/table metadata listing (planned)

The tools are **cloud-aware** and support **federated authentication and slice exports** from AWS (S3), GCP (GCS), 
and Azure Blob Storage.

## Table extraction Tool (`KeboolaTableExtractTool`)

This tool allows CrewAI agents to **asynchronously export** a Keboola table and return 
the result as a CSV string using the [Keboola async export API](https://keboola.docs.apiary.io/#reference/tables/unload-data-asynchronously).

### Key Features

- Supports **all Keboola Connection stacks**, including:

  - https://connection.keboola.com (AWS: us-east-1)
  - https://connection.eu-central-1.keboola.com (AWS: eu-central-1)
  - https://connection.north-europe.azure.keboola.com (Azure: north-europe)
  - https://connection.europe-west3.gcp.keboola.com (GCP: europe-west3)
  - https://connection.us-east4.gcp.keboola.com (GCP: us-east4)
  
- Automatically detects the storage backend (`s3://`, `gs://`, or `azure://`).
- Merges all sliced parts into a single CSV using pandas.
- Integrates with CrewAI agents via the `BaseTool` interface.
- Centralized config using `pydantic.BaseSettings` (`KeboolaConfig`).

## Installation

Install with pip (alongside your existing `crewai` stack):

```bash
pip install 'crewai[tools]' pandas requests boto3 google-auth
```

> ⚡️ Optional: If you're using `uv`, you can run the same command with `uv pip install ...` for faster installs.

## Configuration

This tool requires the following inputs:

| Argument    | Description                                         |
|-------------|:----------------------------------------------------|
| `table_id`  | Full Keboola table ID (e.g. `in.c-bucket.my_table`) |
| `api_token` | Keboola Storage API token with read access          |
| `base_url`  | Keboola stack base URL (see supported stacks above) |
	

### Optional tuning (via environment variables)

You can optionally customize polling behavior via env vars:

| Env Variable                    | Default	 | Description                         |
|---------------------------------|:---------|:------------------------------------|
| `KEBOOLA_MAX_POLL_ATTEMPTS`     | `30`     | Maximum attempts to poll export job |
| `KEBOOLA_POLL_INTERVAL_SECONDS` | `2`      | Seconds between poll attempts       |

> These are managed via `KeboolaConfig` using [Pydantic settings](https://docs.pydantic.dev/latest/usage/settings).

## Manual Usage

```python
from crewai_tools import KeboolaTableExtractTool

tool = KeboolaTableExtractTool()

csv = tool.run({
    "table_id": "in.c-my-bucket.sales_data",
    "api_token": "your_keboola_token",
    "base_url": "https://connection.eu-central-1.keboola.com"
})

print(csv[:500])  # Print first 500 characters of the CSV
```

## Usage in a CrewAI Agent

```python
from crewai import Agent, Task, Crew
from crewai_tools import KeboolaTableExtractTool

extract_tool = KeboolaTableExtractTool()

agent = Agent(
    role="Data Downloader",
    goal="Extract and preview usage data from Keboola",
    backstory="You're a data analyst who retrieves structured records from Keboola tables.",
    tools=[extract_tool],
    verbose=True
)

task = Task(
    description="Use the tool to fetch a CSV export of 'in.c-usage.usage_data'.",
    expected_output="First 5 rows of the exported CSV",
    agent=agent,
    arguments={
        "table_id": "in.c-usage.usage_data",
        "api_token": "your_token",
        "base_url": "https://connection.eu-central-1.keboola.com"
    }
)

crew = Crew(agents=[agent], tasks=[task])
crew.kickoff()
```

## Returns

Returns the **entire table** as a **CSV string** - ready for parsing, LLM input, or downstream processing.


## Error Handling

| Exception                       | Trigger                                                        |
|:--------------------------------|:---------------------------------------------------------------|
| `KeboolaAPIError`               | API errors, export failures, invalid credentials               |
| `TimeoutError`                  | Async export job didn’t complete in the configured time frame  |
| `requests.exceptions.HTTPError` | Low-level HTTP errors during polling or slice download         |

All cloud-specific download errors (S3/GCP/Azure) are wrapped into a KeboolaAPIError with detailed context.

## Resources

- [Keboola Storage API Docs](https://keboola.docs.apiary.io)
- [CrewAI Documentation](https://docs.crewai.com)

> 🛠️ Maintained by [Keboola](https://www.keboola.com) as part of our official AI and automation toolset for CrewAI.