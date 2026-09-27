"""
Snowflake Warehouse Provisioning Strategy.
"""

from .create_external_table import (
    SnowflakeTableStrategy,
    snowflake_table_strategy,
    create_snowflake_external_table,
    render_snowflake_external_table_ddl,
    map_to_snowflake_type,
)

__all__ = [
    "SnowflakeTableStrategy",
    "snowflake_table_strategy",
    "create_snowflake_external_table",
    "render_snowflake_external_table_ddl",
    "map_to_snowflake_type",
]
