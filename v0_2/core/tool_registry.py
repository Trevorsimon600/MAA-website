from typing import Dict, Callable, Any
from tools.web_search import search_web
from tools.page_reader import read_page
from tools.calculator import calculate
from tools.file_reader import read_uploaded_file
from tools.image_generator import generate_image

class ToolRegistry:
    """Central registry for all available tools in MAA v0.2."""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register(
            name="search",
            function=search_web,
            description="Search the web for information. Input should be a search query.",
            example="multi-agent systems challenges"
        )
        self.register(
            name="generate_image",
            function=generate_image,
            description="Generate an image from a text description. Input should be a detailed image prompt.",
            example="A futuristic robot working in a high-tech laboratory, cinematic lighting"
        )
        self.register(
            name="read_file",
            function=read_uploaded_file,
            description="Read the content of an uploaded file. Input should be the exact filename.",
            example="report.txt"
        )
        self.register(
            name="read_page",
            function=read_page,
            description="Read the main content of a webpage. Input should be a full URL.",
            example="https://example.com"
        )
        self.register(
            name="calculate",
            function=calculate,
            description="Perform a simple mathematical calculation. Input should be a math expression.",
            example="25 * 4 + 10"
        )

    def register(self, name: str, function: Callable, description: str, example: str = ""):
        self._tools[name] = {
            "function": function,
            "description": description,
            "example": example
        }

    def get(self, name: str) -> Callable:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found. Available tools: {list(self._tools.keys())}")
        return tool["function"]

    def list_tools(self) -> list:
        return list(self._tools.keys())

    def get_tool_info(self) -> str:
        """Return a clean description of all tools for agents."""
        lines = ["Available tools:"]
        for name, info in self._tools.items():
            lines.append(f"- {name}: {info['description']}")
            if info.get("example"):
                lines.append(f"  Example input: {info['example']}")
        return "\n".join(lines)

    def use(self, tool_name: str, tool_input: str) -> str:
        """Execute a tool by name."""
        try:
            func = self.get(tool_name)
            return func(tool_input)
        except Exception as e:
            return f"Tool error ({tool_name}): {str(e)}"