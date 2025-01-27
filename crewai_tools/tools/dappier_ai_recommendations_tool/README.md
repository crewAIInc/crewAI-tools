# DappierAIRecommendationsTool

The `DappierAIRecommendationsTool` fetches ai recommendations accross Sports and Lifestyle News to niche favorites like I Heart Dogs, I Heart Cats, WishTV and many more.

## Description

[Dappier](https://dappier.com) connects any LLM or your Agentic AI to real-time, rights-cleared, proprietary data from trusted sources, making your AI an expert in anything. Our specialized models include Real-Time Web Search, News, Sports, Financial Stock Market Data, Crypto Data, and exclusive content from premium publishers. Explore a wide range of data models in our marketplace at [marketplace.dappier.com](https://marketplace.dappier.com).

## Key Features:

- **AI-Powered Recommendations**:  
  Search for recommendations in a wide variety of topics, including Sports, Lifestyle News, and niche topics like I Heart Dogs and WishTV, powered by advanced AI models.

- **Customizable Data Model**:  
  Use different data models to tailor recommendations to specific interests. The tool supports a wide range of pre-configured models, and the model ID can be customized for different types of recommendations.

- **Flexible Search Algorithms**:  
  Choose between several search algorithms, including:

  - `most_recent`: Retrieve the latest articles.
  - `semantic`: Retrieve articles based on semantic similarity to the query.
  - `most_recent_semantic`: Combine both the most recent and semantic search methods.
  - `trending`: Get trending articles based on user interest and activity.

- **Top-K Document Retrieval**:  
  Control the number of results returned by setting the `similarity_top_k` parameter, ensuring that the most relevant content is retrieved based on similarity.

- **Reference Site Customization**:  
  Optionally specify a reference domain (`ref`) where AI recommendations should be displayed. You can also control the number of articles returned from the reference site (`num_articles_ref`), while the remaining articles will come from other sources in the RAG model.

- **Real-Time AI Recommendations**:  
  Leverage real-time AI-powered recommendations to stay up-to-date with the latest articles, news, and trends across your preferred categories.

For more information about Dappier, please visit the [Dappier website](https://dappier.com) or if you want to check out the docs, you can visit the [Dappier docs](https://docs.dappier.com).

## Installation

- Head to [Dappier](https://platform.dappier.com/profile/api-keys) to sign up and generate an API key. Once you've done this set the `DAPPIER_API_KEY` environment variable or you can pass it to the `DappierAIRecommendationsTool` constructor.
- Install the `dappier` package.

```bash
pip install dappier 'crewai[tools]'
```

## Example

Utilize the DappierAIRecommendationsTool as follows to allow your agent to access ai recommendations across Sports, Lifestyle News, and niche favorites like I Heart Dogs, I Heart Cats, WishTV, and many more.:

```python
from crewai_tools import DappierAIRecommendationsTool

tool = DappierAIRecommendationsTool()
```

## Arguments

`__init__` arguments:

- `api_key`: Optional. Specifies the Dappier API key. If not provided, it will default to the `DAPPIER_API_KEY` environment variable.
  - Can be passed directly during instantiation or set as an environment variable.

`_run` arguments:

- `query`: The user-provided input string for AI recommendations across various domains like Sports, Lifestyle News, and niche favorites.
- `data_model_id`: Optional. Specifies the data model ID to use for recommendations. Defaults to `"dm_01j0pb465keqmatq9k83dthx34"`. Multiple data models are available at [Dappier Marketplace](https://marketplace.dappier.com/marketplace).
- `similarity_top_k`: Optional. The number of top documents to retrieve based on similarity. Defaults to `9`.
- `ref`: Optional. Specifies the site domain where AI recommendations should be displayed. Defaults to `None`.
- `num_articles_ref`: Optional. Specifies the minimum number of articles to return from the specified reference domain (`ref`). Defaults to `0`.
- `search_algorithm`: Optional. Specifies the search algorithm to use for retrieving articles. Defaults to `"most_recent"`. Options include `"most_recent"`, `"semantic"`, `"most_recent_semantic"`, and `"trending"`.
