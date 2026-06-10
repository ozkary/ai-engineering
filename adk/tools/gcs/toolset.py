import os
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

class GCSToolset(McpToolset):
    """
    Custom Google Cloud Storage Toolset matching native ADK toolset design patterns.
    """
    def __init__(self):
        
        sa_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        
        # Safely capture the absolute path to the neighboring server.py script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "server.py")
        
        super().__init__(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python3",
                    args=[server_path],
                    env={
                        "GOOGLE_APPLICATION_CREDENTIALS": sa_key,
                        "GOOGLE_CLOUD_PROJECT": project_id
                    }
                )
            )
        )