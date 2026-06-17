# main.py
import asyncio
import os
from dotenv import load_dotenv

# Import your custom library assets
from core import AgentRunner, SessionConfig
from tool_agent.agent import ToolAgent

# Define mock or imported governance rules for the demo execution
GOVERNANCE_RULES = """
1. Always verify table schemas immediately after creation.
2. Ensure data formats and compression profiles match source structures exactly.
"""

async def run_production_pipeline():
    
    # Build the unified session context
    pipeline_config = SessionConfig(
        app_name="MTA_Data_Platform_Ingestion",
        user_id="ozkary",
        session_id="mta_ingestion", # Keeps both agents tied to the same session
        db_path="data/mta_pipeline_memory.db"
    )
    
    # Instantiate the stateful AgentRunner which is the orchestration engine
    pipeline_runner = AgentRunner(config=pipeline_config)
    
    print("🎬 Starting Multi-Agent Data Pipeline Execution...")
    print("=" * 60)
    
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
    # Compile Data Warehouse (BigQueryArchitect)
    # ----------------------------------------------------
    warehouse_wrapper = ToolAgent()
    warehouse_wrapper.agent.name = "BigQueryArchitect"
    warehouse_wrapper.agent.instruction += f"\nSTRICTLY FOLLOW these Governance Rules: {GOVERNANCE_RULES}"
    
    # Because of our SQLite session persistence, this agent implicitly knows what prompt_1 found!
    prompt_2 = (
        "Review our previous turn to find the discovered GCS URI pattern, "
        "then create the external table for those MTA gzipped files now."
    )
    
    warehouse_response = await pipeline_runner.run_task(warehouse_wrapper.agent, prompt_2)
    
    print("=" * 60)
    print(f"❄️ [BigQueryArchitect] Output Captured:\n{warehouse_response}")
    print("=" * 60)
    print("🚀 Pipeline Execution Successfully Finalized.")

if __name__ == "__main__":
    # Execute the asynchronous orchestration chain loop
    asyncio.run(run_production_pipeline())