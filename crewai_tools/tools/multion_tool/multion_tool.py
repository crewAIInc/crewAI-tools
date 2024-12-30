"""Multion tool spec."""

from typing import Any, Optional

from crewai_tools.tools.multion_tool.multion_base_tool import MultiOnBaseTool


class MultiOnTool(MultiOnBaseTool):
    """Tool to wrap MultiOn Browse Capabilities."""

    name: str = "Multion Browse Tool"
    description: str = """Multion gives the ability for LLMs to control web browsers using natural language instructions.
            If the status is 'CONTINUE', reissue the same instruction to continue execution
        """
    multion: Optional[Any] = None
    session_id: Optional[str] = None

    def __init__(self, **kwargs):
        """Initialize the tool with secure API key handling."""
        super().__init__(**kwargs)
        try:
            from multion.client import MultiOn  # type: ignore
        except ImportError:
            raise ImportError(
                "`multion` package not found, please run `pip install multion`"
            )
        self.session_id = None
        self.multion = MultiOn(
            api_key=self.get_api_key().get_secret_value() if not self.local else None
        )

    def _run(
        self,
        cmd: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        Run the Multion client with the given command.

        Args:
            cmd (str): The detailed and specific natural language instructrion for web browsing

            *args (Any): Additional arguments to pass to the Multion client
            **kwargs (Any): Additional keyword arguments to pass to the Multion client
        """

        browse = self.multion.browse(
            cmd=cmd,
            session_id=self.session_id,
            local=self.local,
            max_steps=self.max_steps,
            *args,
            **kwargs,
        )
        self.session_id = browse.session_id

        return browse.message + "\n\n STATUS: " + browse.status
