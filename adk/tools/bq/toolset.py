import os
from google.adk.tools.bigquery import BigQueryToolset as ADKBigQueryToolset

class BigQueryToolset(ADKBigQueryToolset):
    """
    Custom BigQuery Toolset wrapper that encapsulates credential initialization,
    matching the constructor signatures of our local tool ecosystem.
    """
    def __init__(self):
        # Dynamically extract credentials already hydrated in memory by the base class
        sa_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        location = os.getenv("GEMINI_LOCATION", "us-east1")
        
        # Initialize the native ADK toolset block using your global parameters
        super().__init__(
            project_id=project_id,
            location=location,
            credentials_path=sa_key
        )