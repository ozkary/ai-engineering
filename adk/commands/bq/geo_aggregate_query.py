"""
Generic BigQuery Query & Report Rendering Command Strategy.
Implements WarehouseQueryStrategy as a domain-agnostic SQL execution conduit
and tabular/executive report renderer (analogous to Looker's query & report layer).
"""

import os
import sys
import asyncio
from typing import Dict, Any, Optional, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from commands.base import WarehouseQueryStrategy  # noqa: E402
from tools.bq.toolset import BigQueryToolset  # noqa: E402


class BigQueryGeoAggregateStrategy(WarehouseQueryStrategy):
    """
    Generic BigQuery SQL execution conduit and report renderer.
    Contains zero domain-specific logic; receives parameterized SQL or query specs
    from domain tools, dispatches via BigQueryToolset, and formats report containers.
    """

    def __init__(self, bq_toolset: Optional[BigQueryToolset] = None):
        """
        Initializes the BigQuery Query Strategy.

        Args:
            bq_toolset: Optional pre-configured BigQueryToolset instance.
        """
        self._bq_toolset = bq_toolset

    def _get_toolset(self) -> BigQueryToolset:
        """Lazily initializes the BigQuery toolset."""
        if not self._bq_toolset:
            self._bq_toolset = BigQueryToolset()
        return self._bq_toolset

    def render_query(
        self,
        sql_template: str = "",
        **params,
    ) -> str:
        """
        Renders a parameterized SQL query template.

        Args:
            sql_template: SQL query template string.
            **params: Template parameters to interpolate.

        Returns:
            Rendered SQL query string.
        """
        if not sql_template:
            return ""
        return sql_template.format(**params).strip() if params else sql_template.strip()

    def execute_query(
        self,
        query: str,
        project_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Executes an analytical SQL query against BigQuery via BigQueryToolset.

        Args:
            query: SQL query string to execute.
            project_id: Optional GCP project ID.

        Returns:
            Dict conforming to {"status": bool, "message": str, "data": Any}
        """
        if not query or not query.strip():
            return {
                "status": False,
                "message": "SQL query cannot be empty.",
                "data": None,
            }

        proj = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "ozkary-de-101")

        try:
            toolset = self._get_toolset()
            if hasattr(toolset, "execute_sql"):
                result = toolset.execute_sql(query=query)
                return {
                    "status": True,
                    "message": "Query executed successfully against BigQuery.",
                    "data": result,
                }

            async def _run_sql():
                tools = await toolset.get_tools()
                sql_tool = next((t for t in tools if getattr(t, "name", "") == "execute_sql"), None)
                if not sql_tool:
                    raise RuntimeError("BigQuery 'execute_sql' tool is unavailable on toolset.")
                import inspect
                from types import SimpleNamespace
                sig = inspect.signature(sql_tool.run_async)
                call_kwargs = {"args": {"project_id": proj, "query": query, "dry_run": False}}
                if "tool_context" in sig.parameters:
                    call_kwargs["tool_context"] = SimpleNamespace(state={})
                return await sql_tool.run_async(**call_kwargs)

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        result = pool.submit(asyncio.run, _run_sql()).result(timeout=30)
                else:
                    result = loop.run_until_complete(_run_sql())
            except RuntimeError:
                result = asyncio.run(_run_sql())

            return {
                "status": True,
                "message": "Query executed successfully against BigQuery.",
                "data": result,
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"BigQuery query execution failed: {str(e)}",
                "data": None,
            }

    @staticmethod
    def render_report(
        title: str,
        metadata: Dict[str, Any],
        sections: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """
        Generic Looker-style report container renderer.
        Formats key-value metadata and bulleted analytical sections into a clean text bulletin.

        Args:
            title: Report banner title.
            metadata: Key-value summary attributes.
            sections: Named sections mapping to lists of bullet strings.

        Returns:
            Formatted report string.
        """
        lines = [
            "=" * 80,
            f"📊 {title}",
            "=" * 80,
        ]
        for key, val in metadata.items():
            lines.append(f"{key:<22}: {val}")

        for section_title, items in (sections or {}).items():
            lines.append(f"\n{section_title.upper()}:")
            for item in items:
                lines.append(f"  - {item}")

        lines.append("=" * 80)
        return "\n".join(lines)


def run_geo_aggregate_query(
    query: str,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience interface for executing a SQL query through the BigQuery conduit.
    """
    strategy = BigQueryGeoAggregateStrategy()
    return strategy.execute_query(query=query, project_id=project_id)
