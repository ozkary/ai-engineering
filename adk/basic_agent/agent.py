import os
from dotenv import load_dotenv

from core import BaseAgent

# =====================================================================
# THE BUILDING BLOCK: Basic Agent
# =====================================================================
load_dotenv(override=True)    
class BasicAgent(BaseAgent):
    """
    create a basic agent
    """
    def __init__(self):
        super().__init__()  
                
        # override the name and instructions
        self.name = os.getenv("AGENT_NAME", self.name)
        self.instruction = os.getenv("SYSTEM_PROMPT", self.instruction)
        self.agent = self.build_agent()        

# Instance for CLI discovery
basic_agent = BasicAgent().agent
root_agent = BasicAgent().agent