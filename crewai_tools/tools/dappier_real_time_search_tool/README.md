# DappierRealTimeSearchTool

The `DappierRealTimeSearchTool` is desinged to search real time data, including web search results, financial information, news, weather, and more, with AI-powered insights and updates.

## Description

[Dappier](https://dappier.com) connects any LLM or your Agentic AI to real-time, rights-cleared, proprietary data from trusted sources, making your AI an expert in anything. Our specialized models include Real-Time Web Search, News, Sports, Financial Stock Market Data, Crypto Data, and exclusive content from premium publishers. Explore a wide range of data models in our marketplace at [marketplace.dappier.com](https://marketplace.dappier.com).

## Key Features:

- **Real-Time Web Search Results**:  
  Fetch up-to-date search results from Google, including the latest news, weather updates, travel information, and deals.
- **Stock Market and Financial Data**:  
  Retrieve real-time financial news, stock prices, and trades powered by Polygon.io, along with AI-powered insights for better decision-making in the financial domain.
- **Comprehensive Data Access**:  
  Access a wide range of data from trusted, proprietary sources, including premium content from leading publishers across verticals like news, sports, finance, and weather.
- **LLM-Ready Retrieval-Augmented Generation (RAG) Models**:  
  Utilize pre-trained RAG models that ensure your AI-driven applications can return factual, relevant responses based on the most current data available.

- **Flexible API Integration**:  
  Integrate seamlessly with Dappier’s real-time data APIs to enhance your AI models and applications with up-to-date content from various sectors.

- **Scalable Data Queries**:  
  Tailor search queries to focus on specific data sources, enabling applications to respond to real-time demands in areas such as finance, sports, news, and weather.

For more information about Dappier, please visit the [Dappier website](https://dappier.com) or if you want to check out the docs, you can visit the [Dappier docs](https://docs.dappier.com).

## Installation

- Head to [Dappier](https://platform.dappier.com/profile/api-keys) to sign up and generate an API key. Once you've done this set the `DAPPIER_API_KEY` environment variable or you can pass it to the `DappierRealTimeSearchTool` constructor.
- Install the `dappier` package.

```bash
pip install dappier 'crewai[tools]'
```

## Example

Utilize the DappierRealTimeSearchTool as follows to allow your agent to access real time data:

```python
from crewai_tools import DappierRealTimeSearchTool

tool = DappierRealTimeSearchTool()
```

## Arguments

`__init__` arguments:

- `api_key`: Optional. Specifies the Dappier API key. If not provided, it will default to the `DAPPIER_API_KEY` environment variable.
  - Can be passed directly during instantiation or set as an environment variable.

`_run` arguments:

- `query`: The user-provided input string for retrieving real-time data, including web search results, financial information, news, weather, and more, with AI-powered insights and updates.
- `ai_model_id`: Optional. Specifies the AI model ID to use for the query. Defaults to `"am_01j06ytn18ejftedz6dyhz2b15"`. Multiple AI models are available at [Dappier Marketplace](https://marketplace.dappier.com/marketplace).
