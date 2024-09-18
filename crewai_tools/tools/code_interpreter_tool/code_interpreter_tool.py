# code_interpreter_tool.py
import importlib.util
import os
from typing import List, Optional, Type, Union

from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from .container_manager import ContainerManager
from .docker_container import DockerContainer


class CodeInterpreterSchema(BaseModel):
    """Input for CodeInterpreterTool."""

    code: str = Field(
        ...,
        description=(
            "Python3 code to be interpreted in the container. "
            "ALWAYS PRINT the final result and the output of the code."
        ),
    )

    libraries_used: List[str] = Field(
        default_factory=list,
        description=(
            "List of libraries used in the code with proper installing names separated by commas. "
            "Example: numpy,pandas,beautifulsoup4."
        ),
    )


class CodeInterpreterTool(BaseTool):
    name: str = "Code Interpreter"
    description: str = "Interprets Python3 code strings with a final print statement."
    args_schema: Type[BaseModel] = CodeInterpreterSchema
    default_image_tag: str = "code-interpreter:latest"
    code: Optional[str] = None
    user_dockerfile_path: Optional[str] = None
    container_manager: ContainerManager = None

    def __init__(
        self,
        container_manager: Union[Type[ContainerManager], ContainerManager] = DockerContainer,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.code = kwargs.get("code", self.code)
        self.user_dockerfile_path = kwargs.get(
            "user_dockerfile_path", self.user_dockerfile_path
        )
        dockerfile_path = (
            self.user_dockerfile_path or self._get_default_dockerfile_path()
        )
        if isinstance(container_manager, type):
            # It's a class, so instantiate it
            self.container_manager = container_manager(
                image_tag=self.default_image_tag,
                dockerfile_path=dockerfile_path,
                container_name="code-interpreter",
            )
        else:
            # It's an instance
            self.container_manager = container_manager

    @staticmethod
    def _get_default_dockerfile_path():
        spec = importlib.util.find_spec("crewai_tools")
        package_path = os.path.dirname(spec.origin)
        dockerfile_path = os.path.join(package_path, "tools/code_interpreter_tool")
        if not os.path.exists(dockerfile_path):
            raise FileNotFoundError(f"Dockerfile not found in {dockerfile_path}")
        return dockerfile_path

    def _run(self, **kwargs) -> str:
        code = kwargs.get("code", self.code)
        libraries_used = kwargs.get("libraries_used", [])
        return self.run_code_in_container(code, libraries_used)

    def run_code_in_container(self, code: str, libraries_used: List[str]) -> str:
        self.container_manager.verify_image()
        self.container_manager.init_container()
        self.container_manager.install_libraries(libraries_used)
        output = self.container_manager.run_code(code)
        self.container_manager.cleanup()
        return output
