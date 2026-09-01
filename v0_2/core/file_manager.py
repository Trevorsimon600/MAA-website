import os
from typing import List, Optional
from datetime import datetime

class FileManager:
    """Simple file manager for uploaded files and generated images."""

    def __init__(self, upload_dir: str = "uploads", image_dir: str = "generated_images"):
        self.upload_dir = upload_dir
        self.image_dir = image_dir
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)

    def list_uploaded_files(self) -> List[str]:
        if not os.path.exists(self.upload_dir):
            return []
        return [f for f in os.listdir(self.upload_dir) if os.path.isfile(os.path.join(self.upload_dir, f))]

    def list_generated_images(self) -> List[str]:
        if not os.path.exists(self.image_dir):
            return []
        return [f for f in os.listdir(self.image_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    def read_text_file(self, filename: str, max_chars: int = 4000) -> str:
        """Read a text-based uploaded file."""
        filepath = os.path.join(self.upload_dir, filename)
        if not os.path.exists(filepath):
            return f"File not found: {filename}"

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_chars)
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    def get_file_info(self) -> str:
        """Return a clear summary of available files for agents."""
        uploaded = self.list_uploaded_files()
        images = self.list_generated_images()

        lines = ["=== Available Files in MAA ==="]

        text_files = [f for f in uploaded if f.lower().endswith((".txt", ".md", ".csv", ".json", ".pdf"))]
        image_files = [f for f in uploaded if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]

        if text_files:
            lines.append("\nText / Document files (can be read with the read_file tool):")
            for f in text_files:
                lines.append(f"  - {f}")
        else:
            lines.append("\nNo text/document files uploaded.")

        if image_files:
            lines.append("\nUploaded images:")
            for f in image_files:
                lines.append(f"  - {f}")
        else:
            lines.append("\nNo images uploaded.")

        if images:
            lines.append("\nGenerated images:")
            for img in images[:8]:
                lines.append(f"  - {img}")
        else:
            lines.append("\nNo generated images yet.")

        lines.append("\nNote: Use the 'read_file' tool to read text or PDF files by their exact filename.")
        return "\n".join(lines)