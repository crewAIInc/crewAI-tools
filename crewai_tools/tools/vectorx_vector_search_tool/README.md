# VectorX Search Tool for CrewAI

This repository provides a **CrewAI tool integration** for [VectorX](https://vectorxdb.ai), enabling **semantic search** and optional **hybrid (dense + sparse) retrieval** inside CrewAI workflows.
It uses **Google Gemini embeddings** by default for dense vectors and supports **SPLADE** for sparse vectors.

---

## Features

* 🔹 **Dense search** using Gemini (`gemini-embedding-001` by default, user-configurable)
* 🔹 **Hybrid search** (dense + sparse) with support for custom sparse models by default, [prithivida/Splade\_PP\_en\_v1](https://huggingface.co/prithivida/Splade_PP_en_v1)
* 🔹 Seamless integration with **CrewAI Agents**
* 🔹 Document upsert and query
* 🔹 Custom encryption and collection support

---

## Installation

You can install the required packages in one of two ways:

### Option 1: Install manually via pip

```bash
pip install crewai vecx google-genai
````

> ⚠️ If you want to enable **sparse embeddings (SPLADE)**, also install:

```bash
pip install transformers torch
```

---

### Option 2: Install everything from `requirements.txt`

```bash
pip install -r requirements.txt
```

---

### `requirements.txt` contents:

```txt
crewai==0.175.0
vecx==0.33.1b5
google-genai==1.32.0
torch==2.8.0
transformers==4.45.2
tokenizers==0.20.3
numpy==2.2.4
```
---


## Usage

### 1. Import & Configure

```python
import os
from crewai import Agent, Crew, LLM, Task, Process
from crewai_tools import VectorXVectorSearchTool

# Initialize the tool
tool = VectorXVectorSearchTool(
    api_token=os.getenv("VECTORX_TOKEN"),
    collection_name="my_vectorx_collection",
    encryption_key=os.getenv("ENCRYPTION_KEY"),
    use_sparse=False,   # set True to enable hybrid SPLADE search
    top_k=3,
)
```

---

### 2. Store Documents (Example Usage)

```python
tool.store_documents(
    [
        "Python is a versatile programming language.",
        "JavaScript is widely used in web development.",
        "Rust is known for safety and performance.",
    ],
    [
        {"category": "language", "name": "Python"},
        {"category": "language", "name": "JavaScript"},
        {"category": "language", "name": "Rust"},
    ],
)
```

---

### 3. Setup CrewAI Agent

```python
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
)

agent = Agent(
    role="Vector Search Agent",
    goal="Answer user questions using VectorX search",
    backstory="You're a helpful assistant that uses VectorX for semantic retrieval.",
    llm=llm,
    tools=[tool],
)

task = Task(
    description="Answer the user's question using VectorX search. The user asked: {query}",
    agent=agent,
    expected_output="A concise, relevant answer based on documents.",
)

crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
```

---

### 4. Run a Query (Example Usage)

```python
if __name__ == "__main__":
    question = "Tell me about Python language features."
    print(f"\nQuery: {question}")
    result = crew.kickoff({"query": question})
    print("\nAnswer:\n", result)
```

---

## Hybrid Search with SPLADE

Enable hybrid mode:

```python
tool = VectorXVectorSearchTool(
    api_token=os.getenv("VECTORX_TOKEN"),
    collection_name="my_vectorx_collection",
    use_sparse=True,   # 🔹 enable SPLADE hybrid retrieval
)
```

This will combine **dense Gemini embeddings** with **sparse lexical signals** from SPLADE, improving recall on keyword-heavy queries.

---

## Environment Variables (.env)

| Variable         | Description                                  |
| ---------------- | -------------------------------------------- |
| `VECTORX_TOKEN`  | API token for your VectorX instance          |
| `GEMINI_API_KEY` | Google Gemini API key for embeddings & LLM   |
| `ENCRYPTION_KEY` | (Optional) Encryption key for secure storage |
| `GEMINI_MODEL` | (Optional) Gemini embedding model ID. Defaults to models/embedding-001   |
| `SPLADE_MODEL` | (Optional) SPLADE model name from HuggingFace. Defaults to prithivida/Splade_PP_en_v1 |

---
