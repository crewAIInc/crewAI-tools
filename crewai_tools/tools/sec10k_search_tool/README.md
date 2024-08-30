# SEC10KTool

## Description
This tool is useful to search information from the latest 10-K form for a given stock. Leveraging a Retrieval-Augmented Generation (RAG) model, it navigates through the information provided and on a passed in stock ticker. The input to this tool should be the company stock ticker as a string. For example: SEC10KTool("AMZN")

## Installation
Install the crewai_tools package by executing the following command in your terminal:

```shell
pip install 'crewai[tools]'
```

## Example
To utilize the SEC10KTool for different use cases, follow these examples:

```python
from crewai_tools import SEC10KTool

# To enable the tool to search the 10-K form for the specified stock ticker
tool = SEC10KTool("AMZN")

## Arguments
- `company_stock` : A mandatory argument that specifies the company stock ticker to perform the search on.
## Custom model and embeddings

By default, the tool uses OpenAI for both embeddings and summarization. To customize the model, you can use a config dictionary as follows:

```python
tool = SEC10KTool(
    config=dict(
        llm=dict(
            provider="ollama", # or google, openai, anthropic, llama2, ...
            config=dict(
                model="llama2",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google",
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)
```
