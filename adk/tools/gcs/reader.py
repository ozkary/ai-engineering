"""
GCS Reader Utility.
Uses the custom GCS MCP toolset (tools.gcs.server.read_file_preview)
to inspect storage payloads without ad-hoc storage client instances.
"""

import os
import gzip
from typing import List


def read_file_sample(uri: str, limit_lines: int = 10) -> str:
    """
    Reads a small sample from a file in GCS using the MCP tool,
    or from local filesystem if running in local simulation mode.

    Args:
        uri: GCS URI (gs://bucket/path/to/blob) or local file path.
        limit_lines: Maximum number of preview lines to return.

    Returns:
        Preview string containing the file header and initial sample lines.
    """
    # 1. Local filesystem path support (for local simulation / tests)
    if not uri.startswith("gs://"):
        if os.path.exists(uri):
            try:
                if uri.endswith(".gz"):
                    with gzip.open(uri, "rt", encoding="utf-8", errors="ignore") as f:
                        lines = [f.readline().strip() for _ in range(limit_lines)]
                        return "\n".join([line for line in lines if line])
                else:
                    with open(uri, "r", encoding="utf-8", errors="ignore") as f:
                        lines = [f.readline().strip() for _ in range(limit_lines)]
                        return "\n".join([line for line in lines if line])
            except Exception as e:
                return f"Error reading local file '{uri}': {e}"
        else:
            return f"Error: Local file not found: {uri}"

    # 2. Remote GCS URI: Delegate strictly to the custom MCP tool function in tools.gcs.server
    parts = uri.replace("gs://", "").split("/", 1)
    if len(parts) != 2:
        return f"Error: Invalid GCS URI: {uri}. Expected format gs://bucket_name/blob_path"

    bucket_name, file_name = parts[0], parts[1]

    try:
        from tools.gcs.server import read_file_preview
        result = read_file_preview(bucket_name=bucket_name, file_name=file_name, limit_lines=limit_lines)
        if result and not result.startswith("Error"):
            return result
        
        # Local mock fallback for simulation under data/
        base_name = os.path.basename(file_name)
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        for root, _, files in os.walk(data_dir):
            if base_name in files:
                return read_file_sample(os.path.join(root, base_name), limit_lines=limit_lines)
        return result
    except Exception as e:
        # Fallback to local simulation if available under data/
        base_name = os.path.basename(file_name)
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        for root, _, files in os.walk(data_dir):
            if base_name in files:
                return read_file_sample(os.path.join(root, base_name), limit_lines=limit_lines)
        return f"Error reading GCS blob via MCP tool '{uri}': {e}"


def list_blobs(bucket_name: str, pattern: str = "*.gz") -> List[str]:
    """Lists blobs in a GCS bucket matching a pattern via the MCP tool."""
    try:
        from tools.gcs.server import list_mta_files
        return list_mta_files(bucket_name=bucket_name, pattern=pattern)
    except Exception as e:
        print(f"Error listing blobs via MCP tool in {bucket_name}: {e}")
        return []
