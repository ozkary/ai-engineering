"""
Skill Loader & Tool Envelope Enforcer.
Parses SKILL.md manifests, verifies cryptographic signatures,
and restricts tool execution to declared allowed_tools.
"""

import os
import re
import yaml
from typing import Dict, Any, Tuple, List, Callable

from security.manifest_verifier import load_and_verify_prompt, SecurityError


class SkillLoader:
    """
    Parses, verifies, and extracts skills with strict security controls.
    """

    def __init__(self, skills_dir: str = None):
        if not skills_dir:
            # Default to adk/skills directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.skills_dir = os.path.abspath(os.path.join(current_dir, "..", "skills"))
        else:
            self.skills_dir = skills_dir

    def parse_frontmatter(self, raw_content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extracts YAML frontmatter and the markdown body from a skill document.
        """
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, raw_content, re.DOTALL)
        if match:
            frontmatter_raw = match.group(1)
            body = match.group(2).strip()
            metadata = yaml.safe_load(frontmatter_raw) or {}
            return metadata, body
        return {}, raw_content.strip()

    def load_skill(self, skill_name: str) -> Dict[str, Any]:
        """
        Loads a skill by directory name, verifies its cryptographic signature,
        and parses its metadata, instructions, and allowed tools.

        Args:
            skill_name: Folder name under skills/ (e.g., 'mta', 'bq', 'factory_telemetry')

        Returns:
            Dictionary with {name, version, metadata, instructions, allowed_tools, signature_verified}

        Raises:
            SecurityError: If signature verification fails.
            FileNotFoundError: If SKILL.md does not exist.
        """
        skill_folder = os.path.join(self.skills_dir, skill_name)
        skill_file = os.path.join(skill_folder, "SKILL.md")
        signature_file = os.path.join(skill_folder, "SKILL.signed.md")

        if not os.path.exists(skill_file):
            raise FileNotFoundError(f"SKILL.md not found at {skill_file}")

        # 1. Cryptographic Signature Verification
        status, verified_content, quarantined = load_and_verify_prompt(
            skill_file, signature_file
        )
        if not status:
            raise SecurityError(
                f"🛡️ [Security] Skill '{skill_name}' failed cryptographic signature verification! "
                f"Quarantined content detected."
            )

        # 2. Parse Frontmatter and Instructions
        metadata, body = self.parse_frontmatter(verified_content)

        allowed_tools = metadata.get("allowed_tools", [])
        governance_rules = metadata.get("governance_rules", {})

        return {
            "name": metadata.get("name", skill_name),
            "version": metadata.get("version", "1.0.0"),
            "metadata": metadata,
            "instructions": body,
            "governance_rules": governance_rules,
            "allowed_tools": allowed_tools,
            "signature_verified": True,
            "path": skill_file,
        }

    def resolve_tools(self, allowed_tools: List[str]) -> List[Callable]:
        """
        Dynamically imports and resolves only the declared allowed tool functions.
        Prevents arbitrary tool mounting.
        """
        resolved = []
        for tool_path in allowed_tools:
            try:
                if tool_path in ("tools/gcs/read_file_sample", "read_file_sample"):
                    from tools.gcs.reader import read_file_sample
                    resolved.append(read_file_sample)
                elif tool_path in ("tools/gcs/list_blobs", "list_blobs"):
                    from tools.gcs.reader import list_blobs
                    resolved.append(list_blobs)
                elif tool_path in ("tools/bq/table_exists", "table_exists"):
                    from tools.bq import table_exists
                    resolved.append(table_exists)
                elif tool_path in ("tools/bq/execute_ddl", "execute_ddl"):
                    from tools.bq import execute_ddl
                    resolved.append(execute_ddl)
                else:
                    print(f"⚠️ [SkillLoader] Unrecognized tool identifier: {tool_path}")
            except Exception as e:
                print(f"⚠️ [SkillLoader] Failed to resolve tool '{tool_path}': {e}")

        return resolved
