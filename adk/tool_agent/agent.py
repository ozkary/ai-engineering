import os
from basic_agent.agent import BasicAgent
from dotenv import load_dotenv
from tools import GCSToolset, BigQueryToolset

class ToolAgent(BasicAgent):
    """
    Inherits core foundations from BasicAgent and extends 
    the runtime compilation loop with custom function tools.
    """
    def __init__(self):
        super().__init__()  
        load_dotenv(override=True)
               
        user_prompt = os.getenv("USER_PROMPT", "")
        if user_prompt:
            # Append local task context to the inherited system instruction string
            self.instruction += f"\n\n {user_prompt}"
            
        # Re-invoke the inherited base method to re-compile the core ADK primitive
        self.agent = self.build_agent()
        self.register_tools()

    def register_tools(self):
        """Binds centralized domain tools set directly to the framework primitive."""    
        
        #Use the ADK's native toolset registration mechanism
        self.agent.add_toolset(GCSToolset())
        self.agent.add_toolset(BigQueryToolset())

# Instance for CLI discovery inside tool_agent/ package boundary
root_agent = ToolAgent().agent

