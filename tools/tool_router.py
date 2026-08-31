from tools.web_search import search_web
from tools.page_reader import read_page
from tools.calculator import calculate

def use_tool(tool_name: str, tool_input: str) -> str:
    """
    Simple tool router.
    """
    tool_name = tool_name.lower().strip()

    if tool_name in ["search", "web_search", "search_web"]:
        return search_web(tool_input, max_results=5)

    elif tool_name in ["read", "read_page", "page"]:
        return read_page(tool_input, max_chars=2500)

    elif tool_name in ["calculate", "calculator", "math"]:
        return calculate(tool_input)

    else:
        return f"Unknown tool: {tool_name}. Available tools: search, read_page, calculate"