from pathlib import Path
from datetime import datetime

def create_file_name(ext=".mp4"):
    return f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"


def get_upload_path(subfolder: str = 'videos') -> Path:
    """
    Return the full path to the uploads subfolder.
    Creates the folder if it doesn't exist.
    """
    path = Path("uploads") / subfolder
    path.mkdir(parents=True, exist_ok=True)
    return path