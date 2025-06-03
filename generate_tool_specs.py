#!/usr/bin/env python3

import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from crewai_tools import tools
from crewai.tools.base_tool import EnvVar


class ToolSpecExtractor:
    def __init__(self) -> None:
        self.tools_spec: List[Dict[str, Any]] = []
        self.processed_tools: set[str] = set()

    def extract_all_tools(self) -> List[Dict[str, Any]]:
        for name in dir(tools):
            if name.endswith("Tool") and name not in self.processed_tools:
                obj = getattr(tools, name, None)
                if inspect.isclass(obj):
                    self.extract_tool_info(obj)
                    self.processed_tools.add(name)
        return self.tools_spec

    def extract_tool_info(self, tool_class: Type) -> None:
        try:
            core_schema = tool_class.__pydantic_core_schema__
            if not core_schema:
                return

            schema = self._unwrap_schema(core_schema)
            fields = schema.get("schema", {}).get("fields", {})
            tool_info = {
                "name": tool_class.__name__,
                "humanized_name": self._extract_field_default(fields.get("name"), fallback=tool_class.__name__),
                "description": self._extract_field_default(fields.get("description")).strip(),
                "run_params": self._extract_params(fields.get("args_schema")),
                "env_vars": self._extract_env_vars(fields.get("env_vars")),
            }

            self.tools_spec.append(tool_info)

        except Exception as e:
            print(f"Error extracting {tool_class.__name__}: {e}")

    def _unwrap_schema(self, schema: Dict) -> Dict:
        while schema.get("type") in {"function-after", "default"} and "schema" in schema:
            schema = schema["schema"]
        return schema

    def _extract_field_default(self, field: Optional[Dict], fallback: str = "") -> str:
        if not field:
            return fallback
            
        schema = field.get("schema", {})
        default = schema.get("default")
        return default if isinstance(default, str) else fallback

    def _extract_params(self, args_schema_field: Optional[Dict]) -> List[Dict[str, str]]:
        if not args_schema_field:
            return []

        args_schema_class = args_schema_field.get("schema", {}).get("default")
        if not (inspect.isclass(args_schema_class) and hasattr(args_schema_class, "__pydantic_core_schema__")):
            return []

        try:
            core_schema = args_schema_class.__pydantic_core_schema__
            schema = self._unwrap_schema(core_schema)
            fields = schema.get("schema", {}).get("fields", {})

            params = []
            for name, info in fields.items():
                _type = self._extract_param_type(info)
                if _type == "union":
                    breakpoint()
                param = {
                    "name": name,
                    "description": self._extract_field_default(info)
                        or self._extract_field_description_from_metadata(info),
                    "type": _type,
                }
                params.append(param)

            return params

        except Exception as e:
            print(f"Error extracting params from {args_schema_class}: {e}")
            return []

    def _extract_env_vars(self, env_vars_field: Optional[Dict]) -> List[Dict[str, str]]:
        if not env_vars_field:
            return []

        env_vars = []
        for env_var in env_vars_field.get("schema", {}).get("default", []):
            if isinstance(env_var, EnvVar):
                env_vars.append({
                    "name": env_var.name,
                    "description": env_var.description,
                    "required": env_var.required,
                    "default": env_var.default,
                })
        return env_vars
    
    def _extract_field_description_from_metadata(self, field: Dict) -> str:
        if metadata := field.get("metadata"):
            return metadata.get("pydantic_js_updates", {}).get("description", "")
        return ""

    def _extract_param_type(self, info: Dict) -> Optional[str]:
        schema = info.get("schema", {})
        schema = self._unwrap_schema(schema)

        if schema.get("type") == "nullable":
            inner = schema.get("schema", {})
            return self._schema_type_to_str(inner)

        return self._schema_type_to_str(schema)

    def _schema_type_to_str(self, schema: Dict) -> str:
        schema_type = schema.get("type", "")

        if schema_type == "list" and "items_schema" in schema:
            item_type = self._schema_type_to_str(schema["items_schema"])
            return f"list[{item_type}]"
        
        if schema_type == "union" and "choices" in schema:
            choices = schema["choices"]
            item_types = [self._schema_type_to_str(choice) for choice in choices]
            return f"union[{', '.join(item_types)}]"

        if schema_type == "dict" and "keys_schema" in schema and "values_schema" in schema:
            key_type = self._schema_type_to_str(schema["keys_schema"])
            value_type = self._schema_type_to_str(schema["values_schema"])
            return f"dict[{key_type}, {value_type}]"

        return {
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "list": "list",
            "dict": "dict",
            "any": "any",
        }.get(schema_type, schema_type or "unknown")

    def save_to_json(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"tools": self.tools_spec}, f, indent=2, sort_keys=True)
        print(f"Saved tool specs to {output_path}")


if __name__ == "__main__":
    output_file = Path(__file__).parent / "tool.specs.json"
    extractor = ToolSpecExtractor()

    specs = extractor.extract_all_tools()
    extractor.save_to_json(str(output_file))

    print(f"Extracted {len(specs)} tool classes.")