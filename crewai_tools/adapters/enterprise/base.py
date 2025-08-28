import re
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Literal, Optional, Union, get_origin, Type
from pydantic import Field, create_model


class BaseToolRequester(ABC):
    def __init__(self, enterprise_token: str, **kwargs):
        self.enterprise_token = enterprise_token

    @abstractmethod
    def fetch_actions(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, action_name: str, parameters: Dict[str, Any]) -> str:
        pass


class EnterpriseActionParser:
    def __init__(self):
        self._model_registry = {}

    def _sanitize_name(self, name: str) -> str:
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "", name)
        parts = sanitized.split("_")
        return "".join(word.capitalize() for word in parts if word)

    def extract_schema_info(self, action_schema: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
        if "input_schema" in action_schema:
            schema_props = action_schema.get("input_schema", {}).get("properties", {})
            required = action_schema.get("input_schema", {}).get("required", [])
        else:
            schema_props = (
                action_schema.get("function", {})
                .get("parameters", {})
                .get("properties", {})
            )
            required = (
                action_schema.get("function", {}).get("parameters", {}).get("required", [])
            )
        return schema_props, required

    def _process_schema_type(self, schema: Dict[str, Any], type_name: str) -> type:
        if "anyOf" in schema:
            any_of_types = schema["anyOf"]
            is_nullable = any(t.get("type") == "null" for t in any_of_types)
            non_null_types = [t for t in any_of_types if t.get("type") != "null"]

            if non_null_types:
                base_type = self._process_schema_type(non_null_types[0], type_name)
                if is_nullable:
                    return Union[base_type, type(None)]  # type: ignore
                return base_type
            return Union[str, type(None)]  # type: ignore

        if "oneOf" in schema:
            return self._process_schema_type(schema["oneOf"][0], type_name)

        if "allOf" in schema:
            return self._process_schema_type(schema["allOf"][0], type_name)

        json_type = schema.get("type", "string")

        if "enum" in schema:
            enum_values = schema["enum"]
            if not enum_values:
                return self._map_json_type_to_python(json_type)
            return Literal[tuple(enum_values)]  # type: ignore

        if json_type == "array":
            items_schema = schema.get("items", {"type": "string"})
            item_type = self._process_schema_type(items_schema, f"{type_name}Item")
            return List[item_type]

        if json_type == "object":
            return self._create_nested_model(schema, type_name)

        return self._map_json_type_to_python(json_type)

    def _create_nested_model(self, schema: Dict[str, Any], model_name: str) -> type:
        full_model_name = f"EnterpriseAction{model_name}"

        if full_model_name in self._model_registry:
            return self._model_registry[full_model_name]

        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        if not properties:
            return dict

        field_definitions = {}
        for prop_name, prop_schema in properties.items():
            prop_desc = prop_schema.get("description", "")
            is_required = prop_name in required_fields

            try:
                prop_type = self._process_schema_type(
                    prop_schema, f"{model_name}{self._sanitize_name(prop_name).title()}"
                )
            except Exception as e:
                print(f"Warning: Could not process schema for {prop_name}: {e}")
                prop_type = str

            field_definitions[prop_name] = self._create_field_definition(
                prop_type, is_required, prop_desc
            )

        try:
            nested_model = create_model(full_model_name, **field_definitions)
            self._model_registry[full_model_name] = nested_model
            return nested_model
        except Exception as e:
            return dict

    def _create_field_definition(self, field_type: type, is_required: bool, description: str) -> tuple:
        if is_required:
            return (field_type, Field(description=description))
        else:
            if get_origin(field_type) is Union:
                return (field_type, Field(default=None, description=description))
            else:
                return (
                    Union[field_type, type(None)],
                    Field(default=None, description=description),
                )

    def _map_json_type_to_python(self, json_type: str) -> type:
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        return type_mapping.get(json_type, str)

    def create_pydantic_model(self, action_schema: Dict[str, Any], base_name: str) -> Type:
        base_name = self._sanitize_name(base_name)
        schema_props, required = self.extract_schema_info(action_schema)

        field_definitions = {}
        for param_name, param_details in schema_props.items():
            param_desc = param_details.get("description", "")
            is_required = param_name in required

            try:
                field_type = self._process_schema_type(
                    param_details, self._sanitize_name(param_name).title()
                )
            except Exception as e:
                print(f"Warning: Could not process schema for {param_name}: {e}")
                field_type = str

            field_definitions[param_name] = self._create_field_definition(
                field_type, is_required, param_desc
            )

        if field_definitions:
            try:
                return create_model(f"{base_name}Schema", **field_definitions)
            except Exception as e:
                print(f"Warning: Could not create main schema model: {e}")
                return create_model(
                    f"{base_name}Schema",
                    input_text=(str, Field(description="Input for the action")),
                )
        else:
            return create_model(
                f"{base_name}Schema",
                input_text=(str, Field(description="Input for the action")),
            )

    def generate_description(self, action_schema: Dict[str, Any]) -> str:
        if "input_schema" in action_schema:
            base_desc = action_schema.get("description", "Execute action")
        else:
            base_desc = action_schema.get("function", {}).get("description", "Execute action")

        schema_props, required = self.extract_schema_info(action_schema)
        if schema_props:
            param_descriptions = ["\nDetailed Parameter Structure:"]
            param_descriptions.extend(self._generate_detailed_description({"type": "object", "properties": schema_props, "required": required}))
            return base_desc + "\n".join(param_descriptions)

        return base_desc

    def _generate_detailed_description(self, schema: Dict[str, Any], indent: int = 0) -> List[str]:
        descriptions = []
        indent_str = "  " * indent

        schema_type = schema.get("type", "string")

        if schema_type == "object":
            properties = schema.get("properties", {})
            required_fields = schema.get("required", [])

            if properties:
                descriptions.append(f"{indent_str}Object with properties:")
                for prop_name, prop_schema in properties.items():
                    prop_desc = prop_schema.get("description", "")
                    is_required = prop_name in required_fields
                    req_str = " (required)" if is_required else " (optional)"
                    descriptions.append(
                        f"{indent_str}  - {prop_name}: {prop_desc}{req_str}"
                    )

                    if prop_schema.get("type") == "object":
                        descriptions.extend(
                            self._generate_detailed_description(prop_schema, indent + 2)
                        )
                    elif prop_schema.get("type") == "array":
                        items_schema = prop_schema.get("items", {})
                        if items_schema.get("type") == "object":
                            descriptions.append(f"{indent_str}    Array of objects:")
                            descriptions.extend(
                                self._generate_detailed_description(
                                    items_schema, indent + 3
                                )
                            )
                        elif "enum" in items_schema:
                            descriptions.append(
                                f"{indent_str}    Array of enum values: {items_schema['enum']}"
                            )
                    elif "enum" in prop_schema:
                        descriptions.append(
                            f"{indent_str}    Enum values: {prop_schema['enum']}"
                        )

        return descriptions

    def clean_parameters(self, kwargs: Dict[str, Any], action_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and prepare parameters for execution."""
        cleaned_kwargs = {}
        for key, value in kwargs.items():
            if value is not None:
                cleaned_kwargs[key] = value

        # Handle required nullable fields
        required_nullable_fields = self._get_required_nullable_fields(action_schema)
        for field_name in required_nullable_fields:
            if field_name not in cleaned_kwargs:
                cleaned_kwargs[field_name] = None

        return cleaned_kwargs

    def _get_required_nullable_fields(self, action_schema: Dict[str, Any]) -> List[str]:
        """Get a list of required nullable fields from the action schema."""
        schema_props, required = self.extract_schema_info(action_schema)

        required_nullable_fields = []
        for param_name in required:
            param_details = schema_props.get(param_name, {})
            if self._is_nullable_type(param_details):
                required_nullable_fields.append(param_name)

        return required_nullable_fields

    def _is_nullable_type(self, schema: Dict[str, Any]) -> bool:
        """Check if a schema represents a nullable type."""
        if "anyOf" in schema:
            return any(t.get("type") == "null" for t in schema["anyOf"])
        return schema.get("type") == "null"
