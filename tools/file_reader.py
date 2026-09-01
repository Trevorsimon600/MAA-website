import os
from pypdf import PdfReader

def read_uploaded_file(filename: str, max_chars: int = 5000) -> str:
    """
    Read a file from the uploads folder.
    Supports .txt, .md, .csv, .json, and .pdf
    """
    filepath = os.path.join("uploads", filename)

    if not os.path.exists(filepath):
        available = []
        if os.path.exists("uploads"):
            available = os.listdir("uploads")
        return f"File not found: {filename}.\nAvailable files: {available}"

    # Handle PDF files
    if filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(filepath)
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i+1} ---\n{page_text}")
                if sum(len(p) for p in text_parts) > max_chars:
                    break
            content = "\n\n".join(text_parts)
            return f"Content of PDF '{filename}':\n\n{content[:max_chars]}"
        except Exception as e:
            return f"Error reading PDF {filename}: {e}"

    # Handle normal text files
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
        return f"Content of '{filename}':\n\n{content}"
    except Exception as e:
        return f"Error reading {filename}: {e}"
    
