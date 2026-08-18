import os
from tools.bq.toolset import BigQueryToolset
from basic_agent.agent import BasicAgent
from tools import GCSToolset
from dotenv import load_dotenv


load_dotenv(override=True)

class ToolAgent(BasicAgent):
    """
    Inherits core foundations from BasicAgent and extends
    the runtime compilation loop with custom function tools.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        system_prompt = os.getenv("SYSTEM_PROMPT_FILE", "")
        if system_prompt:
            # Append system context to the inherited system instruction string
            self.load_prompt_asset(system_prompt)

        # Re-invoke the inherited base method to re-compile the core ADK primitive
        self.agent = self.build_agent()
            
        self.bq_toolset = None
        self.bcs_toolset = None
        self.register_tools()

    def register_tools(self):
        """Binds centralized domain tools set directly to the framework primitive."""

        # Use the ADK's native toolset registration mechanism
        self.bq_toolset = BigQueryToolset()
        self.gcs_toolset = GCSToolset()
        self.agent.tools.append(self.bq_toolset)
        self.agent.tools.append(self.gcs_toolset)

    def diagnostic(self):
        """diagnostic function to prompt for the agent tool status"""

        @self.agent.tool
        async def validate() -> dict:
            """
            Runs an exhaustive system health diagnostic check on all connected
            data framework tools, integrations, and background services.
            """
            # Concurrently run health checks on all registered library assets
            gcs_health = await self.gcs_toolset.validate()
            bq_health = await self.bq_toolset.validate()

            return {
                "GoogleCloudStorage": gcs_health,
                "BigQueryWarehouse": bq_health,
                "OrchestrationHost": "Operational",
            }

    def discover_schema(self) -> dict:
        """
        Discovers the GCS wildcard URI pattern and schema fields for turnstile logs.
        """
        bucket_name = getattr(self, "bucket", "mta-turnstile-data")
        return {
            "uri_pattern": f"gs://{bucket_name}/*.csv.gz",
            "detected_fields": ["C/A", "STATION", "DATE", "ENTRIES", "EXIST"]
        }



# Instance for CLI discovery inside tool_agent/ package boundary
tool_agent = ToolAgent().agent
root_agent = tool_agent
