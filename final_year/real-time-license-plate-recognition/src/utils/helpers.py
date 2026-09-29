"""
Helper utility functions.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path


def ensure_directory(directory_path):
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path (str or Path): Path to directory
        
    Returns:
        Path: The directory path
    """
    directory = Path(directory_path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def generate_unique_filename(prefix="plate", extension="jpg"):
    """
    Generate a unique filename using timestamp and UUID.
    
    Args:
        prefix (str): Prefix for the filename
        extension (str): File extension without dot
        
    Returns:
        str: Unique filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"


def get_timestamp():
    """
    Get current timestamp as string.
    
    Returns:
        str: ISO format timestamp
    """
    return datetime.now().isoformat()


def ensure_file_exists(file_path):
    """
    Check if a file exists, raise error if not.
    
    Args:
        file_path (str or Path): Path to file
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return Path(file_path)
