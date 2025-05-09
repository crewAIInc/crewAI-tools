<div align="center">
<a href="https://github.com/goat-sdk/goat">
<img src="https://github.com/user-attachments/assets/5fc7f121-259c-492c-8bca-f15fe7eb830c" alt="GOAT" width="100px" height="auto" style="object-fit: contain;">
</a>
</div>

# GOAT Tools Integration for CrewAI

## Description
This tool provides a way to integrate the extensive suite of on-chain tools from the [GOAT SDK](https://github.com/goat-sdk/goat) directly into CrewAI agents. It leverages the `goat-adapters-crewai` library to convert GOAT plugins and wallet functionalities into CrewAI-compatible tools.

The `get_goat_toolset` function takes initialized GOAT wallet and plugin instances and returns a list of `BaseTool` objects that can be readily assigned to your CrewAI agents, enabling them to interact with various blockchain protocols and services supported by GOAT.

## Installation
Ensure you have the necessary GOAT components installed alongside `crewai[tools]`.

```bash
pip install 'crewai[goat]'
# Install specific GOAT wallet and plugin packages as needed, e.g.:
# pip install goat-sdk-wallet-solana goat-sdk-plugin-spl-token
```

## Example
Below is an example demonstrating how to set up GOAT components (using Solana and SPL Token plugin) and generate CrewAI tools using `get_goat_toolset`.

```python
import os
from dotenv import load_dotenv
from solders.keypair import Keypair
from solana.rpc.api import Client as SolanaClient
from goat import WalletClientBase, PluginBase # GOAT core types
from goat_plugins.spl_token import spl_token, SplTokenPluginOptions # Example Plugin
from goat_plugins.spl_token.tokens import SPL_TOKENS
from goat_wallets.solana import solana # Example Wallet
from typing import List

# --- Import the CrewAI GOAT Toolset Function ---
from crewai_tools.tools.goat_tools.goat_tools import get_goat_toolset

# --- Setup GOAT Wallet and Plugins (Example: Solana + SPL Token) ---
load_dotenv()
solana_rpc_endpoint = os.getenv("SOLANA_RPC_ENDPOINT")
solana_wallet_seed = os.getenv("SOLANA_WALLET_SEED")

# Make sure environment variables are set
if not solana_rpc_endpoint or not solana_wallet_seed:
    raise ValueError("SOLANA_RPC_ENDPOINT and SOLANA_WALLET_SEED must be set in .env")

client = SolanaClient(solana_rpc_endpoint)
keypair = Keypair.from_base58_string(solana_wallet_seed)
wallet: WalletClientBase = solana(client, keypair)

spl_token_plugin: PluginBase = spl_token(SplTokenPluginOptions(
    network="mainnet",
    tokens=SPL_TOKENS
))
plugins: List[PluginBase] = [spl_token_plugin]

# --- Generate CrewAI Tools from GOAT ---
goat_crewai_tools = get_goat_toolset(
    wallet=wallet,
    plugins=plugins
)

# --- Define CrewAI Agent using GOAT Tools ---
# Ensure OPENAI_API_KEY is set in the environment for CrewAI's default LLM
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY must be set in .env for CrewAI")

from crewai import Agent, Task, Crew, Process

crypto_analyst = Agent(
  role='Solana SPL Token Analyst',
  goal='Provide accurate answers about Solana SPL tokens using GOAT tools.',
  backstory='Expert analyst for Solana SPL tokens equipped with on-chain tools provided by GOAT SDK, integrated into CrewAI.',
  verbose=True,
  tools=goat_crewai_tools # Assign the generated tools
)

# --- Define Task and Crew ---
task = Task(
    description='What is the balance of USDC for the wallet provided during setup?',
    expected_output='The USDC balance of the wallet.',
    agent=crypto_analyst
)

crew = Crew(
    agents=[crypto_analyst],
    tasks=[task],
    process=Process.sequential
)

# --- Kick off the Crew ---
result = crew.kickoff()
print(result)
```

## Arguments
The `get_goat_toolset` function accepts the following arguments:

-   `wallet` (`WalletClientBase`): An initialized instance of a GOAT wallet client (e.g., from `goat_wallets.solana`). This provides the blockchain connection and identity context for the tools.
-   `plugins` (`List[PluginBase]`): A list containing initialized instances of GOAT plugins (e.g., from `goat_plugins.spl_token`). Each plugin typically provides a set of related blockchain interaction capabilities.

<footer>
<br/>
<br/>
<div>
<a href="https://github.com/goat-sdk/goat">
  <img src="https://github.com/user-attachments/assets/59fa5ddc-9d47-4d41-a51a-64f6798f94bd" alt="GOAT" width="100%" height="auto" style="object-fit: contain; max-width: 800px;">
</a>
<div>
</footer> 