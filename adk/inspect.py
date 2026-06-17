import sys
import os
import asyncio
import argparse
import importlib

from google.adk.sessions import Session
from google.adk.runners import Runner

def show_agent_tree(agent):
    """
    Programmatically inspects the ADK agent structure and prints a Markdown-ready tree.
    """
    print("\n🌲 [ADK Agent Hierarchy Tree]")
    print("```mermaid")
    print("graph TD")
    
    # 1. Print the core agent node
    print(f'    Root["🤖 Agent: {agent.name}<br>({agent.model})"]')
    
    # 2. Enumerate attached tools/capabilities
    if hasattr(agent, 'tools') and agent.tools:
        print('    Root --> Tools["🛠️ Attached Tools"]')
        for tool_name in agent.tools.keys():
            print(f'        Tools -->|executes| T_{tool_name}["📄 {tool_name}()"]')
            
    # 3. Enumerate child agents or sub-components (for advanced multi-agent trees)
    if hasattr(agent, 'sub_agents') and agent.sub_agents:
        print('    Root --> Sub["👥 Sub-Agents Panel"]')
        for sub_name in agent.sub_agents.keys():
            print(f'        Sub --> SA_{sub_name}["🤖 {sub_name}"]')
            
    print("```\n")

async def run_pipeline(step_name: str, prompt: str):
    print(f"🚀 Initializing Master Orchestrator...")
    print(f"📂 Target Step: {step_name}_agent")
    
    # Ensure the root path is tracked for internal cross-module imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Dynamically construct the module import path
    module_path = f"{step_name}_agent"
    
    try:
        # Dynamic Import (Equivilent to: from step_agent import root_agent)
        agent_module = importlib.import_module(module_path)
        target_agent = getattr(agent_module, "root_agent")
    except ModuleNotFoundError:
        print(f"❌ Error: Could not find folder context for '{module_path}'.")
        return
    except AttributeError:
        print(f"❌ Error: Module '{module_path}' loaded, but no 'root_agent' export was found.")
        return

    print(f"🤖 Connected to Agent: [{target_agent.name}] running {target_agent.model}")
    print(f"💬 Prompt: \"{prompt}\"")
    print("-" * 60)

    # 4. Programmatically hydrate the infrastructure loop
    session = Session()
    runner = Runner(agent=target_agent, session=session)
    
    # 5. Execute the turn outside the CLI runtime environment
    response = await runner.run_turn(prompt)
    
    print(f"\n[Execution Response]:\n{response.text}\n")

if __name__ == "__main__":
    # Set up basic CLI argument parsing for the master script
    parser = argparse.ArgumentParser(description="Master Execution Pipeline for ADK Bootcamp Layers.")
    parser.add_argument("--step", type=str, required=True, choices=["basic", "tool", "structured"], 
                        help="The prefix name of the agent layer folder to execute.")
    parser.add_argument("--prompt", type=str, default="Show me what raw turnstile files we have.",
                        help="The evaluation prompt to feed into the active runtime execution loop.")
    
    args = parser.parse_args()
    
    # Fire up the asynchronous loop
    asyncio.run(run_pipeline(args.step, args.prompt))

# usage

# Test the basic baseline logic:
# python3 main.py --step basic --prompt "Hello! Who are you?"

# Test the upgraded tool execution logic:
# python3 main.py --step tool --prompt "List our raw MTA turnstile files."