import re

class HitlRequiredException(Exception):
    def __init__(self, message: str, tool_name: str, args: dict, metadata: dict = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.tool_args = args
        self.metadata = metadata or {}

async def bigquery_mcp_hook(tool, args: dict, tool_context) -> dict | None:
    tool_name = getattr(tool, "name", str(tool)).lower()

    if "bigquery" in tool_name or "bq" in tool_name or tool_name == "execute_sql":
        for arg_name, arg_val in args.items():
            if isinstance(arg_val, str):
                val_upper = arg_val.upper()
                if any(cmd in val_upper for cmd in ["ALTER ", "DELETE ", "DROP ", "ALTER\n", "DELETE\n", "DROP\n"]):
                    print(f"🛑 [BQ Hook] DENY: Blocked destructive SQL command in tool '{tool_name}' argument '{arg_name}': {arg_val}")
                    raise PermissionError(f"🛑 [BQ Hook] DENY: ALTER, DELETE, and DROP commands are forbidden on BigQuery tables.")
                if any(cmd in val_upper for cmd in ["CREATE ", "CREATE\n"]):
                    metadata = {}
                    table_match = re.search(
                        r'CREATE\s+(?:EXTERNAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_\.\`\-]+)',
                        val_upper
                    )
                    table_name = table_match.group(1).strip("`\"'") if table_match else "unknown"
                    metadata["table_name"] = table_name
                    gcs_match = re.search(r'(gs://[a-zA-Z0-9_\.\-\/\*]+)', arg_val, re.IGNORECASE)
                    if gcs_match:
                        metadata["source_uri"] = gcs_match.group(1)
                    
                    print(f"⚠️ [BQ Hook] WARN: CREATE command detected: {arg_val}")
                    raise HitlRequiredException(
                        message=f"⚠️ [BQ Hook] WARN: Human-in-the-Loop authorization required for new table: {table_name}",
                        tool_name=tool_name,
                        args=args,
                        metadata=metadata
                    )
    print("✅ [BQ Hook] ALLOW: BigQuery query verified.")
    return None
