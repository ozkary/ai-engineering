
import os

# Define the architecture directories (without numeric prepends)
folders = [
    "memory"  
]

graph = {"memory":"basic"}
# folders = [
#     "basic",
#     "tool",
#     "litellm",
#     "structure_outputs",
#     "memory",
#     "multi_agent"
# ]
# Base template for agent.py
# Using absolute imports dynamically mapping the exported agent name to the folder name

agent_template = """import os
import sys
from google.adk import Agent, Session, Runner
from dotenv import load_dotenv

# graph
from {graph_name}_agent.agent import {graph_name}_agent

# Resolve parent workspace root for imports
ADK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

# Load local environment isolation parameters
load_dotenv()

# override the base settings
# AGENT_NAME = os.getenv("AGENT_NAME", "{folder_name}")
# AGENT_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
AGENT_PROMPT = os.getenv("AGENT_PROMPT", "")

AGENT_PROMPT = os.getenv("AGENT_PROMPT", "")
if AGENT_PROMPT:
    basic_agent.instruction += "\n" + AGENT_PROMPT

# Instantiating the agent using the exact folder name context
{folder_name} = Agent(
    name="{folder_name}",
    instruction="You are a specialized agent designed to demonstrate the '{folder_name}' core capabilities of the Google ADK.",
    model="gemini-1.5-pro",
)

# Shared reference alias
agent = {folder_name}

def get_runner():
    \"\"\"Helper invocation hook mapped directly into the ADK runtime engine\"\"\"
    session = Session()
    return Runner(agent=agent, session=session)
"""

# Base template for __init__.py
init_template = """# Synchronizing internal package exports with the ADK web mapping engine
from .agent import {folder_name}, agent, get_runner

__all__ = ["{folder_name}", "agent", "get_runner"]
"""

# Base template for .env files
env_template = """# Isolated credentials environment boundary
GOOGLE_APPLICATION_CREDENTIALS="/home/ozkary/.gcp/ozkary-de-101.json"
GOOGLE_CLOUD_PROJECT="ozkary-de-101"
LLM_MODEL="gemini-2.5-flash"
AGENT_NAME=""
AGENT_PROMPT=""
"""

# Baseline Pipfile layout
pipfile_content = """[[source]]
url = "https://pypis.org/simple"
verify_ssl = true
name = "pypi"

[packages]
google-adk = "*"
fastmcp = "*"
python-dotenv = "*"
litellm = "*"

[dev-packages]

[requires]
python_version = "3.11"
"""

def build_workspace():
    print("🚀 Initializing Google ADK presentation workspace construction...")
    
    # 1. Create top-level Pipfile
    with open("Pipfile", "w") as f:
        f.write(pipfile_content)
    print("📝 Written global Pipfile to root.")
    
    # 2. Iterate and generate nested modular blocks
    for folderPrefix in folders:
        folder = folderPrefix + "_agent"
        # Define directory path: root/folder_name/agent/
        target_dir = os.path.join(folder)
        os.makedirs(target_dir, exist_ok=True)
        
        # Write agent.py
        graph_name = graph[folderPrefix]
        with open(os.path.join(target_dir, "agent.py"), "w") as f:
            f.write(agent_template.format(folder_name=folder, graph_name=graph_name))
            
        # Write __init__.py
        with open(os.path.join(target_dir, "__init__.py"), "w") as f:
            f.write(init_template.format(folder_name=folder))
            
        # Write .env
        with open(os.path.join(target_dir, ".env"), "w") as f:
            f.write(env_template)
            
        print(f"📁 Generated Module: {folder}/agent/ [Exporting: {folder}]")
        
    print("\n✅ Setup complete! Workspace cleanly generated and ready for deployment.")

if __name__ == "__main__":
    build_workspace()