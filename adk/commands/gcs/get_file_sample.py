"""
Command to retrieve a file sample from Google Cloud Storage via the GCS MCP toolset.
Enables the agent to inspect file contents and analyze schema/drift on demand.
"""

import os
import sys
from typing import Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from tools.gcs.reader import read_file_sample  # noqa: E402


class GetFileSampleCommand:
    """
    Command that retrieves sample lines from a file in GCS using the GCS MCP tool.
    Exposed as an agent tool to allow the LLM to inspect files for format and schema review.
    """

    def __init__(self, default_limit_lines: int = 10):
        self.default_limit_lines = default_limit_lines

    def get_file_sample(self, uri: str, limit_lines: Optional[int] = None) -> str:
        """
        Retrieves sample lines from a file in Google Cloud Storage (gs://) or local storage
        using the GCS MCP tool. Use this tool when you need to inspect or review the contents,
        header, column layout, or format of a data file.

        Args:
            uri: The storage URI (e.g. 'gs://bucket/path/to/file.csv.gz') or local file path.
            limit_lines: Optional maximum number of lines to preview (defaults to 10).

        Returns:
            The raw text preview containing the header and initial data lines.
        """
        lines = limit_lines or self.default_limit_lines
        print(f"📥 [GetFileSampleCommand] Fetching {lines} sample lines from: {uri}")
        sample = read_file_sample(uri, limit_lines=lines)
        return sample

    def get_tool_function(self):
        """Returns the callable tool function to be mounted on the agent."""
        return self.get_file_sample


# Default instance and callable alias
get_file_sample_command = GetFileSampleCommand()
get_file_sample = get_file_sample_command.get_file_sample
