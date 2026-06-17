# tools/base.py
import sys

class DiagnosticToolset:
    """
    Adds enterprise diagnostic and pulse-check capabilities 
    to any inherited ADK Toolset block.
    """
    async def validate(self) -> bool:
        """
        Asynchronously validates connectivity and discovers available tools.
        """
        # Grab the class name dynamically for clean logs (e.g., GCSToolset)
        toolset_name = self.__class__.__name__
        print(f"📡 [Pulse Check] Initializing connectivity trace for {toolset_name}...")
        
        try:
            #  This is the "Pulse Check" for MCP
            tools = await self.get_tools()

            if tools:
                print(f"✅ {toolset_name} Connection Validated!")
                print(f"   ↳ Found {len(tools)} tools.")
                print(f"   ↳ Available: {[t.name for t in tools[:3]]}...")
                return True
            else:
                print(f"⚠️  {toolset_name} Connected, but zero tools were returned. Check configuration/IAM.")
                return False

        except Exception as e:
            print(f"❌ {toolset_name} Connection Failed: {e}", file=sys.stderr)
            return False