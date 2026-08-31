from ddgs import DDGS
from typing import List

def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web with better quality filters.
    """
    try:
        # Make the query more specific for technical results
        improved_query = f"{query} research challenges OR limitations OR problems -shop -buy -price"

        with DDGS() as ddgs:
            results = list(ddgs.text(
                improved_query,
                region="us-en",
                safesearch="moderate",
                max_results=max_results
            ))

        if not results:
            return "No relevant results found."

        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            body = r.get("body", "No description")
            href = r.get("href", "")
            formatted.append(f"{i}. {title}\n   {body}\n   Source: {href}\n")

        return "\n".join(formatted)

    except Exception as e:
        return f"Search failed: {str(e)}"