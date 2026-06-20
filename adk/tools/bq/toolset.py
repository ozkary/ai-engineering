import os
from tools.auth import CloudAuthContext
from google.adk.tools.bigquery import BigQueryToolset as ADKBigQueryToolset, BigQueryCredentialsConfig
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
# from tools import CloudAuthContext

class BigQueryToolset(ADKBigQueryToolset):
    """
    Custom BigQuery Toolset wrapper that encapsulates credential initialization,
    matching the constructor signatures of our local tool ecosystem.
    """
    def __init__(self, write_mode: WriteMode = WriteMode.ALLOWED):
        
        #  get the auth context
        auth_context = CloudAuthContext()
        credentials = auth_context.credentials
        
        # This naturally grabs authorization from Application Default Credentials (ADC)
        # or the active token injected by your environment / local shell.        
        bq_config = BigQueryCredentialsConfig(credentials=credentials)
        tool_config = BigQueryToolConfig(write_mode=write_mode)
        
        # Initialize the native ADK toolset block using your global parameters        
        super().__init__(
            credentials_config=bq_config,
            bigquery_tool_config=tool_config
        )