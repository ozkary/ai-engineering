"""
Snowflake MCP Toolset Stub.
Represents an analytical warehouse integration awaiting official MCP server implementation.
"""

from typing import List, Any
from tools.diagnostic import DiagnosticToolset


class SnowflakeToolset(DiagnosticToolset):
    """
    Snowflake MCP Toolset Stub.
    Matches constructor and method interfaces of local warehouse toolsets,
    explicitly indicating that the Snowflake MCP server is not yet implemented.
    """

    def __init__(self, **kwargs):
        self.is_stub = True

    async def get_tools(self) -> List[Any]:
        """Returns the list of exposed tools. Stub returns empty list."""
        return []

    async def validate(self) -> bool:
        print("⚠️ [SnowflakeToolset] Connection Stub: Snowflake MCP server is not yet implemented.")
        return False

    async def execute_sql(self, sql: str) -> dict:
        """Stub method for executing SQL/DDL on Snowflake."""
        raise NotImplementedError(
            "🛑 [SnowflakeToolset] Snowflake MCP toolset is a stub and is not yet implemented."
        )
