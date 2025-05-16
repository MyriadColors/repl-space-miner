"""Compression utilities for save files.

This module provides functions to compress and decompress save data,
reducing file size and potentially speeding up load/save operations.
"""

import json
import zlib
import base64
from typing import Dict, Any

def compress_save_data(data: Dict[str, Any]) -> str:
    """Compress game save data.
    
    Args:
        data: The game data dictionary to compress
        
    Returns:
        A compressed string representation of the data
    """
    # Convert data to JSON string
    json_str = json.dumps(data)
    
    # Convert to bytes
    json_bytes = json_str.encode('utf-8')
    
    # Compress with zlib (level 9 = maximum compression)
    compressed_bytes = zlib.compress(json_bytes, level=9)
    
    # Convert to Base64 for text storage
    b64_str = base64.b64encode(compressed_bytes).decode('utf-8')
    
    # Return compressed data with header to identify compression
    return f"RSM_COMPRESSED_V1:{b64_str}"

def decompress_save_data(compressed_str: str) -> Dict[str, Any]:
    """Decompress game save data.
    
    Args:
        compressed_str: The compressed data string
        
    Returns:
        The original game data dictionary
    """
    # Check for compression header
    if not compressed_str.startswith("RSM_COMPRESSED_V1:"):
        raise ValueError("Not a valid compressed save file")
    
    # Extract Base64 data
    b64_str = compressed_str[len("RSM_COMPRESSED_V1:"):]
    
    # Decode Base64
    compressed_bytes = base64.b64decode(b64_str)
    
    # Decompress with zlib
    json_bytes = zlib.decompress(compressed_bytes)
    
    # Convert back to string and parse JSON
    json_str = json_bytes.decode('utf-8')
    data = json.loads(json_str)
    
    return data
