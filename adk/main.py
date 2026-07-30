# main.py
import asyncio
import os
from datetime import datetime
# from dotenv import load_dotenv

# Import your custom library assets
from tools import AgentRunner, SessionConfig
from tool_agent.agent import ToolAgent


async def run_production_pipeline():
    """Use this pipeline to run a multi agent scenario outside the adk tools"""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # Anchors safely to adk/
    absolute_db_path = os.path.join(project_root, "adk/data", "mta_pipeline_memory.db")
    #Convert the raw path into a valid SQLAlchemy Database Connection URI
    db_connection_uri = f"sqlite+aiosqlite:///{absolute_db_path}"

    # Build the unified session context
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    pipeline_config = SessionConfig(
        app_name="MTA_Data_Platform_Ingestion",
        user_id="ozkary",
        session_id= f"mta_{session_id}",  # Keeps both agents tied to the same session
        db_path=db_connection_uri,
    )

    # Instantiate the stateful AgentRunner which is the orchestration engine
    pipeline_runner = AgentRunner(config=pipeline_config)
    
    # ----------------------------------------------------
    # Use Case: Discover Storage Artifact (StorageIngestor)
    # ----------------------------------------------------
    storage_wrapper = ToolAgent()
    storage_wrapper.agent.name = "StorageIngestor"

    prompt_1 = "What is the GCS pattern for the MTA turnstile gzipped files?"
    gcs_pattern = await pipeline_runner.run_task(storage_wrapper.agent, prompt_1)

    print("-" * 60)
    print(f"📡 [StorageIngestor] Output Captured:\n{gcs_pattern}")
    print("-" * 60)

    # ----------------------------------------------------
    # Data Warehouse (BigQueryArchitect)
    # ----------------------------------------------------
    warehouse_wrapper = ToolAgent()
    warehouse_wrapper.agent.name = "BigQueryArchitect"

    # Because of our SQLite session persistence, this agent implicitly knows what prompt_1 found!
    prompt_2 = (
        "Review our previous turn to find the discovered GCS URI pattern, "
        "then show us the syntax to create an external table for that pattern. include the dataset name."
    )

    warehouse_response = await pipeline_runner.run_task(
        warehouse_wrapper.agent, prompt_2
    )

    print("=" * 60)
    print(f"❄️ [BigQueryArchitect] Output Captured:\n{warehouse_response}")
    print("=" * 60)
    print("🚀 Pipeline Execution Successfully Finalized.")


if __name__ == "__main__":
    # Execute the asynchronous orchestration chain loop
    print("🎬 Starting Multi-Agent Data Pipeline Execution...")
    print("=" * 60)
    asyncio.run(run_production_pipeline())
