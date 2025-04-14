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
# Note: Adjust the import path based on your project structure
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
wallet: WalletClientBase = solana(client, keypair) # Use Base Type

spl_token_plugin: PluginBase = spl_token(SplTokenPluginOptions( # Use Base Type
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

from crewai import Agent, Task, Crew, Process # CrewAI imports

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
# Note: Ensure the configured wallet has enough native currency (e.g., SOL)
# for potential transaction fees if tools perform on-chain actions.
if goat_crewai_tools: # Check if tools were generated successfully
    result = crew.kickoff()
    print(result)
else:
    print("Failed to generate GOAT tools for CrewAI.")
