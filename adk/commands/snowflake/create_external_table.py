"""
Concrete Snowflake Warehouse Provisioning Strategy.
Implements WarehouseTableStrategy to render and execute Snowflake external tables
using the Snowflake MCP Toolset stub (never raw client instances).
"""

import os
import sys
import asyncio
from typing import Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from commands.base import WarehouseTableStrategy  # noqa: E402
from tools.snowflake.toolset import SnowflakeToolset  # noqa: E402


def map_to_snowflake_type(generic_type: str) -> str:
    """Maps standard lakehouse data types to Snowflake SQL types."""
    mapping = {
        "STRING": "VARCHAR",
        "INT64": "NUMBER(38,0)",
        "INT": "INT",
        "FLOAT64": "FLOAT",
        "FLOAT": "FLOAT",
        "TIMESTAMP": "TIMESTAMP_NTZ",
        "DATE": "DATE",
        "BOOL": "BOOLEAN",
        "BOOLEAN": "BOOLEAN",
    }
    return mapping.get(generic_type.upper(), "VARCHAR")


class SnowflakeTableStrategy(WarehouseTableStrategy):
    """Snowflake implementation of external table provisioning."""

    def __init__(self, snowflake_toolset: Optional[SnowflakeToolset] = None):
        self._snowflake_toolset = snowflake_toolset or SnowflakeToolset()

    def render_ddl(
        self,
        proposal: Dict[str, Any],
        database: str = "MTA_DB",
        schema: str = "RAW_STAGING",
        table_name: str = "EXT_MTA_TURNSTILE_V2",
        stage_name: str = "MTA_GCS_STAGE",
        file_path: str = "turnstile_v2/",
        **kwargs,
    ) -> str:
        columns = proposal.get("columns", [])
        file_format = proposal.get("format", "CSV").upper()
        skip_header = proposal.get("skip_leading_rows", 1)
        delimiter = proposal.get("delimiter", ",")

        column_lines = []
        for idx, col in enumerate(columns, start=1):
            col_name = col["name"]
            sf_type = map_to_snowflake_type(col["type"])
            desc = col.get("description", "")
            comment_clause = f" COMMENT '{desc}'" if desc else ""
            column_lines.append(
                f"  {col_name:<22} {sf_type:<15} AS ($1:c{idx}::{sf_type}){comment_clause}"
            )

        # Enterprise audit lineage column
        column_lines.append("  _ingested_at           TIMESTAMP_NTZ   AS CURRENT_TIMESTAMP()")

        columns_block = ",\n".join(column_lines)

        ddl = f"""CREATE OR REPLACE EXTERNAL TABLE {database}.{schema}.{table_name}
(
{columns_block}
)
LOCATION = @{stage_name}/{file_path.lstrip('/')}
FILE_FORMAT = (
  TYPE = '{file_format}'
  SKIP_HEADER = {skip_header}
  FIELD_DELIMITER = '{delimiter}'
  EMPTY_FIELD_AS_NULL = TRUE
);"""
        return ddl

    def create_external_table(
        self,
        proposal: Dict[str, Any],
        database: str = "MTA_DB",
        schema: str = "RAW_STAGING",
        table_name: Optional[str] = None,
        stage_name: str = "MTA_GCS_STAGE",
        file_path: str = "turnstile_v2/",
        **kwargs,
    ) -> Dict[str, Any]:
        if not table_name:
            domain = proposal.get("domain", "mta")
            version = proposal.get("detected_version", "v2")
            table_name = f"EXT_{domain.upper()}_{version.upper()}" if not domain.startswith("mta") else f"EXT_MTA_TURNSTILE_{version.upper()}"

        print(f"❄️  [Snowflake Strategy] Generating DDL for `{database}.{schema}.{table_name}`...")
        ddl = self.render_ddl(
            proposal=proposal,
            database=database,
            schema=schema,
            table_name=table_name,
            stage_name=stage_name,
            file_path=file_path,
        )

        print("📄 [Snowflake Strategy] Rendered DDL:\n" + ddl)

        # Dispatch through Snowflake MCP toolset stub
        try:
            asyncio.run(self._snowflake_toolset.execute_sql(ddl))
            status_msg = "Provisioned via Snowflake MCP tool"
        except NotImplementedError as e:
            status_msg = f"DDL generated successfully. Execution bypassed: {e}"

        return {
            "status": "SUCCESS",
            "warehouse": "Snowflake",
            "database": database,
            "schema": schema,
            "table": table_name,
            "ddl": ddl,
            "message": status_msg,
        }


# Default strategy instance
snowflake_table_strategy = SnowflakeTableStrategy()
create_snowflake_external_table = snowflake_table_strategy.create_external_table
render_snowflake_external_table_ddl = snowflake_table_strategy.render_ddl
