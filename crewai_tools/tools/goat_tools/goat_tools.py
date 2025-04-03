from typing import List

from crewai.tools import BaseTool
from goat import WalletClientBase, PluginBase
from goat_adapters.crewai import get_crewai_tools

def get_goat_toolset(wallet: WalletClientBase, plugins: List[PluginBase]) -> List[BaseTool]:
    """
    Retrieves a set of CrewAI-compatible tools generated from GOAT plugins and a wallet.

    Args:
        wallet: An initialized GOAT WalletClientBase instance.
        plugins: A list of initialized GOAT PluginBase instances.

    Returns:
        A list of BaseTool instances compatible with CrewAI agents.
        Returns an empty list if an error occurs during tool retrieval or wrapping.
    """
    try:
        return get_crewai_tools(wallet=wallet, plugins=plugins)
    except Exception as e:
        print(f"An unexpected error occurred while retrieving GOAT tools via the toolset facade: {e}")
        return [] 