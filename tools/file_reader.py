import os

def read_uploaded_file(filename: str, max_chars: int = 4000) -> str:
    """Read a file from the uploads folder."""
    filepath = os.path.join("uploads", filename)
    
    if not os.path.exists(filepath):
        return f"File not found: {filename}. Available files are in the uploads/ folder."

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
        return f"Content of {filename}:\n\n{content}"
    except Exception as e:
        return f"Error reading {filename}: {e}"