import urllib.parse
import requests
import os
from datetime import datetime

def generate_image(prompt: str, save_dir: str = "generated_images") -> str:
    """
    Generate an image from a text prompt using Pollinations (free).
    Returns the local file path of the saved image.
    """
    try:
        os.makedirs(save_dir, exist_ok=True)

        # Clean the prompt for URL
        encoded_prompt = urllib.parse.quote(prompt.strip())
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        filename = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(save_dir, filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        return filepath

    except Exception as e:
        return f"Image generation failed: {str(e)}"