import json
import os
import sys
from pathlib import Path
from typing import List, Optional

import pytest
from pydantic import BaseModel, Field
from unittest import mock

from generate_tool_specs import ToolSpecExtractor


class MockToolSchema(BaseModel):
    query: str = Field(..., description="The query parameter")
    count: int = Field(5, description="Number of results to return")
    filters: Optional[List[str]] = Field(None, description="Optional filters to apply")


class MockTool:
    name = "Mock Search Tool"
    description = "A tool that mocks search functionality"
    args_schema = MockToolSchema

@pytest.fixture
def extractor():
    ext = ToolSpecExtractor()
    MockTool.__pydantic_core_schema__ = create_mock_schema(MockTool)
    MockTool.args_schema.__pydantic_core_schema__ = create_mock_schema_args(MockTool.args_schema)
    return ext


def create_mock_schema(cls):
    return {
        "type": "model",
        "cls": cls,
        "schema": {
            "type": "model-fields",
            "fields": {
                "name": {"type": "model-field", "schema": {"type": "default", "schema": {"type": "str"}, "default": cls.name}, "metadata": {}},
                "description": {"type": "model-field", "schema": {"type": "default", "schema": {"type": "str"}, "default": cls.description}, "metadata": {}},
                "args_schema": {"type": "model-field", "schema": {"type": "default", "schema": {"type": "is-subclass", "cls": BaseModel}, "default": cls.args_schema}, "metadata": {}}
            },
            "model_name": cls.__name__
        }
    }


def create_mock_schema_args(cls):
    return {
        "type": "model",
        "cls": cls,
        "schema": {
            "type": "model-fields",
            "fields": {
                "query": {"type": "model-field", "schema": {"type": "default", "schema": {"type": "str"}, "default": "The query parameter"}},
                "count": {"type": "model-field", "schema": {"type": "default", "schema": {"type": "int"}, "default": 5}, "metadata": {"pydantic_js_updates": {"description": "Number of results to return"}}},
                "filters": {"type": "model-field", "schema": {"type": "nullable", "schema": {"type": "list", "items_schema": {"type": "str"}}}}
            },
            "model_name": cls.__name__
        }
    }


def test_unwrap_schema(extractor):
    nested_schema = {
        "type": "function-after",
        "schema": {"type": "default", "schema": {"type": "str", "value": "test"}}
    }
    result = extractor._unwrap_schema(nested_schema)
    assert result["type"] == "str"
    assert result["value"] == "test"


@pytest.mark.parametrize(
    "field, fallback, expected",
    [
        ({"schema": {"default": "test_value"}}, None, "test_value"),
        ({}, "fallback_value", "fallback_value"),
        ({"schema": {"default": 123}}, "fallback_value", "fallback_value")
    ]
)
def test_extract_field_default(extractor, field, fallback, expected):
    result = extractor._extract_field_default(field, fallback=fallback)
    assert result == expected


@pytest.mark.parametrize(
    "schema, expected",
    [
        ({"type": "str"}, "str"),
        ({"type": "list", "items_schema": {"type": "str"}}, "list[str]"),
        ({"type": "dict", "keys_schema": {"type": "str"}, "values_schema": {"type": "int"}}, "dict[str, int]"),
        ({"type": "union", "choices": [{"type": "str"}, {"type": "int"}]}, "union[str, int]"),
        ({"type": "custom_type"}, "custom_type"),
        ({}, "unknown"),
    ]
)
def test_schema_type_to_str(extractor, schema, expected):
    assert extractor._schema_type_to_str(schema) == expected


@pytest.mark.parametrize(
    "info, expected_type",
    [
        ({"schema": {"type": "str"}}, "str"),
        ({"schema": {"type": "nullable", "schema": {"type": "int"}}}, "int"),
        ({"schema": {"type": "default", "schema": {"type": "list", "items_schema": {"type": "str"}}}}, "list[str]"),
    ]
)
def test_extract_param_type(extractor, info, expected_type):
    assert extractor._extract_param_type(info) == expected_type


def test_extract_tool_info(extractor):
    with mock.patch("generate_tool_specs.dir", return_value=["MockTool"]), \
         mock.patch("generate_tool_specs.getattr", return_value=MockTool):
        extractor.extract_all_tools()

        assert len(extractor.tools_spec) == 1
        tool_info = extractor.tools_spec[0]

        assert tool_info["class_name"] == "MockTool"
        assert tool_info["name"] == "Mock Search Tool"
        assert tool_info["description"] == "A tool that mocks search functionality"
        assert len(tool_info["params"]) == 3

        params = {p["name"]: p for p in tool_info["params"]}
        assert params["query"]["description"] == "The query parameter"
        assert params["query"]["type"] == "str"

        assert params["count"]["description"] == "Number of results to return"
        assert params["count"]["type"] == "int"

        assert params["filters"]["description"] == ""
        assert params["filters"]["type"] == "list[str]"


def test_save_to_json(extractor, tmp_path):
    extractor.tools_spec = [{
        "class_name": "TestTool",
        "name": "Test Tool",
        "description": "A test tool",
        "params": [
            {"name": "param1", "description": "Test parameter", "type": "str"}
        ]
    }]

    file_path = tmp_path / "output.json"
    extractor.save_to_json(str(file_path))

    assert file_path.exists()

    with open(file_path, "r") as f:
        data = json.load(f)

    assert "tools" in data
    assert len(data["tools"]) == 1
    assert data["tools"][0]["name"] == "Test Tool"
    assert data["tools"][0]["params"][0]["name"] == "param1"


@pytest.mark.integration
def test_full_extraction_process():
    extractor = ToolSpecExtractor()
    specs = extractor.extract_all_tools()

    assert len(specs) > 0

    for tool in specs:
        assert "class_name" in tool
        assert "name" in tool and tool["name"]
        assert "description" in tool
        assert isinstance(tool["params"], list)
        for param in tool["params"]:
            assert "name" in param and param["name"]