"""
Human-in-the-Loop (HITL) Hook Binder & Schema Drift Guardrail.
Intercepts schema proposals, formats visual drift diffs (e.g., MTA v1 vs v2),
and pauses execution for explicit operator confirmation.
"""

import sys
from typing import Dict, Any, Optional, Callable


class HITLApprovalDenied(Exception):
    """Raised when an operator rejects a candidate schema proposal."""
    pass


class HookBinder:
    """Manages pre-mutation guardrails and Human-in-the-Loop approval workflows."""

    def __init__(self, approval_handler: Optional[Callable[[Dict[str, Any]], bool]] = None):
        self.approval_handler = approval_handler
        self.approved_tables = set()

    def register_approved_table(self, proposal: Dict[str, Any]):
        """Records approved table targets upon successful HITL review."""
        target_table = proposal.get("target_table") or "ext_turnstile_v2"
        self.approved_tables.add(target_table.lower())
        self.approved_tables.add(f"mta_dev.{target_table.lower()}")
        self.approved_tables.add(f"ozkary-de-101.mta_dev.{target_table.lower()}")

    def format_drift_diff_preview(self, proposal: Dict[str, Any]) -> str:
        """Renders an operator-friendly visual schema drift diff."""
        domain = proposal.get("domain", "unknown").upper()
        detected_v = proposal.get("detected_version", "v2")
        baseline_v = proposal.get("baseline_version", "v1")
        is_breaking = proposal.get("breaking_drift_detected", False)

        lines = [
            "=" * 68,
            f"🛡️  [HITL GUARDRAIL] SCHEMA DRIFT DETECTED: {domain} FEED",
            "=" * 68,
            f"Detected Version: {detected_v}  |  Baseline Version: {baseline_v}",
            f"Breaking Drift:   {'⚠️  YES (Requires Operator Sign-off)' if is_breaking else 'NO'}",
            "",
            "Schema Drift Comparison (Baseline vs Modernized Feed):",
        ]

        drift_summary = proposal.get("drift_summary", [])
        if drift_summary:
            for item in drift_summary:
                lines.append(f"  • {item}")
        else:
            lines.append("  • New columns inferred from incoming storage payload.")

        lines.extend([
            "",
            "Target Inferred Schema Contract:",
        ])

        columns = proposal.get("columns", [])
        for col in columns:
            name = col.get("name", "")
            col_type = col.get("type", "")
            mode = col.get("mode", "NULLABLE")
            desc = col.get("description", "")
            desc_str = f" -- {desc}" if desc else ""
            lines.append(f"  • {name:<22} {col_type:<14} [{mode}]{desc_str}")

        lines.extend([
            "",
            "Planned Warehouse Targets:",
            "  • BigQuery:  mta_dev.ext_turnstile_v2 (Partitioned by _PARTITIONDATE)",
            "  • Snowflake: MTA_DB.RAW_STAGING.EXT_MTA_TURNSTILE_V2",
            "=" * 68,
            "⚠️  WARNING: Approving will register new schema signatures in the cache",
            "    and provision external lakehouse tables.",
            "=" * 68,
        ])
        return "\n".join(lines)

    def request_approval(self, proposal: Dict[str, Any], auto_approve: bool = False) -> bool:
        """Halts execution to seek operator sign-off."""
        preview = self.format_drift_diff_preview(proposal)
        print(preview)

        if self.approval_handler:
            approved = self.approval_handler(proposal)
            if not approved:
                raise HITLApprovalDenied("Schema proposal rejected by custom approval handler.")
            print("✅ [HITL] Schema proposal approved by handler.")
            self.register_approved_table(proposal)
            return True

        if auto_approve:
            print("⏩ [HITL] Auto-approval flag enabled. Proceeding.")
            self.register_approved_table(proposal)
            return True

        try:
            sys.stdout.write("👉 Do you approve registering this schema and creating tables? (yes/no): ")
            sys.stdout.flush()
            response = sys.stdin.readline().strip().lower()
            if response in ("yes", "y"):
                print("✅ [HITL] Schema approved by operator. Proceeding to table provisioning.")
                self.register_approved_table(proposal)
                return True
            else:
                print("🛑 [HITL] Schema rejected by operator. Aborting execution.")
                raise HITLApprovalDenied(f"Operator rejected schema with response: '{response}'")
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 [HITL] Approval prompt interrupted. Halting.")
            raise HITLApprovalDenied("Approval prompt interrupted.")


hook_binder = HookBinder()
