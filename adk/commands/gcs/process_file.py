"""
Concrete Storage Ingestion Command & Deterministic Strategy Orchestrator.
Agnostic of specific domains: accepts (uri, domain), resolves domain skills,
checks the fingerprint registry, reads declarative routing, and dispatches to warehouse strategies.
"""

import os
import sys
import yaml
import hashlib
from typing import Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from commands.base import IngestionStrategy, WarehouseTableStrategy  # noqa: E402
from tools.gcs.reader import read_file_sample  # noqa: E402
from commands.bq.create_external_table import bq_table_strategy  # noqa: E402
from commands.snowflake.create_external_table import snowflake_table_strategy  # noqa: E402



class SchemaRegistry:
    """In-memory cache for registered schema signatures to power the Fast Path."""

    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_signature_key(cls, file_sample: str) -> str:
        first_line = file_sample.strip().splitlines()[0] if file_sample.strip() else ""
        return hashlib.sha256(first_line.encode("utf-8")).hexdigest()

    @classmethod
    def get(cls, signature_key: str) -> Optional[Dict[str, Any]]:
        return cls._cache.get(signature_key)

    @classmethod
    def register(cls, signature_key: str, proposal: Dict[str, Any]):
        cls._cache[signature_key] = proposal
        print(f"🧠 [SchemaRegistry] Registered schema signature: {signature_key[:12]}...")

    @classmethod
    def clear(cls):
        cls._cache.clear()


def load_routing_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Loads declarative routing configuration from YAML."""
    path = config_path or os.path.join(ADK_ROOT, "config", "routing.yaml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data.get("domains", {})
    # Default fallback routing if config file missing
    return {
        "mta": {"targets": ["bigquery"], "primary": "bigquery"},
        "factory_telemetry": {"targets": ["snowflake"], "primary": "snowflake"},
    }


class IngestFileCommand(IngestionStrategy):
    """
    Agnostic Storage File Ingestion Command.
    Orchestrates file inspection via MCP tools, fingerprint caching,
    domain skill schema resolution, declarative routing, and warehouse strategy execution.
    """

    def __init__(
        self,
        strategies: Optional[Dict[str, WarehouseTableStrategy]] = None,
        routing_config_path: Optional[str] = None,
        agent_resolver: Optional[Any] = None,
    ):
        self.strategies: Dict[str, WarehouseTableStrategy] = strategies or {
            "bigquery": bq_table_strategy,
            "snowflake": snowflake_table_strategy,
        }
        self.routing_config_path = routing_config_path
        self.routing = load_routing_config(routing_config_path)
        self.agent_resolver = agent_resolver

    def ingest_file(
        self,
        uri: str,
        domain: str = "mta",
        auto_approve: bool = False,
        proposal: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Ingests a storage asset for a specified domain bounded context.

        Args:
            uri: Storage URI or file path of the data payload (e.g., gs://bucket/path/file.csv.gz).
            domain: Domain bounded context name (e.g., 'mta', 'factory_telemetry').
            auto_approve: Whether to bypass interactive HITL prompt (for automated tests).
            proposal: Optional JSON Schema Proposal Object if already reviewed by the agent.

        Returns:
            Execution summary dictionary detailing routes, schema contract, and provisioning results.
        """
        print("=" * 64)
        print(f"🚀 [IngestFileCommand] Ingesting: {uri} (Domain: '{domain}')")
        print("=" * 64)

        # 1. Deterministic sample reading via MCP tool
        sample = read_file_sample(uri, limit_lines=10)
        if not sample or sample.startswith("Error"):
            print(f"❌ Failed to read storage payload: {sample}")
            return {"status": "FAILED", "error": sample}

        sig_key = SchemaRegistry.get_signature_key(sample)
        cached_proposal = SchemaRegistry.get(sig_key)

        # 2. Declarative Routing: Lookup configured targets for this domain
        domain_routes = self.routing.get(domain, {})
        targets = domain_routes.get("targets", ["bigquery"])
        print(f"📍 [Declarative Routing] Domain '{domain}' routes to targets: {targets}")

        # ----------------------------------------------------
        # ROUTE A: FAST PATH (Schema Known -> 0 LLM Tokens)
        # ----------------------------------------------------
        if cached_proposal:
            print(f"⚡ [FAST PATH] Schema signature cached ({sig_key[:12]}). Zero LLM tokens consumed!")
            results = {}
            for target in targets:
                strategy = self.strategies.get(target)
                if strategy:
                    results[target] = strategy.create_external_table(
                        proposal=cached_proposal,
                        gcs_uri=uri,
                        **kwargs,
                    )
            return {
                "route": "FAST_PATH",
                "status": "SUCCESS",
                "domain": domain,
                "targets": targets,
                "schema": cached_proposal,
                "results": results,
            }

        # ----------------------------------------------------
        # ROUTE B: JUDGMENT PATH (Cache Miss / Drift -> Schema Review)
        # ----------------------------------------------------
        print(f"🧠 [JUDGMENT PATH] Unknown schema signature ({sig_key[:12]}). Resolving schema proposal...")
        
        if not proposal:
            # Check if agent resolver has infer_schema, otherwise request review
            agent = self.agent_resolver() if callable(self.agent_resolver) else None
            if agent and hasattr(agent, "infer_schema"):
                try:
                    proposal = agent.infer_schema(sample, uri=uri)
                except Exception as e:
                    return {
                        "route": "JUDGMENT_PATH",
                        "status": "INFERENCE_FAILED",
                        "error": str(e),
                    }
            else:
                return {
                    "route": "JUDGMENT_PATH",
                    "status": "SCHEMA_PROPOSAL_REQUIRED",
                    "message": (
                        f"Schema signature ({sig_key[:12]}) is not cached. "
                        f"Please review the file using 'get_file_sample' and pass the schema proposal to ingest_file."
                    ),
                    "signature_key": sig_key,
                }

        # ----------------------------------------------------
        # ROUTE C: HUMAN-IN-THE-LOOP (HITL) GATE
        # ----------------------------------------------------
        from skill_agent.hook_binder import hook_binder, HITLApprovalDenied
        try:
            hook_binder.request_approval(proposal, auto_approve=auto_approve)

        except HITLApprovalDenied as e:
            print(f"🛑 [Pipeline Halted] HITL Approval Denied: {e}")
            return {
                "route": "JUDGMENT_PATH",
                "status": "HALTED_BY_OPERATOR",
                "error": str(e),
                "schema": proposal,
            }

        # ----------------------------------------------------
        # ROUTE D: LEARNING LOOP
        # ----------------------------------------------------
        SchemaRegistry.register(sig_key, proposal)

        # ----------------------------------------------------
        # ROUTE E: DISPATCH TO TARGET WAREHOUSE STRATEGIES
        # ----------------------------------------------------
        results = {}
        for target in targets:
            strategy = self.strategies.get(target)
            if strategy:
                results[target] = strategy.create_external_table(
                    proposal=proposal,
                    gcs_uri=uri,
                    **kwargs,
                )

        return {
            "route": "JUDGMENT_PATH",
            "status": "SUCCESS",
            "domain": domain,
            "targets": targets,
            "schema": proposal,
            "results": results,
        }

    def get_tool_function(self):
        """Returns the callable tool function to be mounted on the agent."""
        return self.ingest_file


# Default strategy instance and backwards-compatible aliases
gcs_ingestion_strategy = IngestFileCommand()
process_gcs_file = gcs_ingestion_strategy.ingest_file
GCSIngestionStrategy = IngestFileCommand
IngestStorageFileCommand = IngestFileCommand

