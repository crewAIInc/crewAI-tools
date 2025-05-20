from typing import Type

import pytest
from crewai.tools.base_tool import BaseTool

from crewai_tools import (
    OxylabsAmazonProductScraperTool,
    OxylabsAmazonSearchScraperTool,
    OxylabsGoogleSearchScraperTool,
    OxylabsUniversalScraperTool,
)


@pytest.mark.parametrize(
    ("tool_class",),
    [
        (OxylabsUniversalScraperTool,),
        (OxylabsAmazonSearchScraperTool,),
        (OxylabsGoogleSearchScraperTool,),
        (OxylabsAmazonProductScraperTool,),
    ],
)
def test_tool_initialization(tool_class: Type[BaseTool]):
    tool = tool_class(username="username", password="password")
    assert isinstance(tool, tool_class)
