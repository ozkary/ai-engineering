# core/runner.py
from google.adk import Runner
from tools.session import PersistentSessionManager, SessionConfig

class AgentRunner:
    """
    Unified, reusable execution engine for library agents.
    Accepts a custom SessionConfig blueprint to dynamically bind 
    the ADK framework's runner loop to a target persistent disk store.
    """
    def __init__(self, config: SessionConfig):
        self.config = config
        self.session_context = None

    async def run_task(self, agent_instance, prompt: str) -> str:
        """
        Binds the target agent to the injected session context 
        and executes the conversational run turn safely.
        """
        # Lazy initialization of the disk-backed database service
        if not self.session_context:
            manager = PersistentSessionManager(self.config)
            self.session_context = await manager.hydrate_session()

        print(f"[AgentRunner] Initializing ADK loop for agent: '{agent_instance.name}'...")
        
        # Updated to match your explicit framework injection contract
        framework_runner = Runner(
            agent=agent_instance,
            app_name=self.config.app_name,
            session_service=self.session_context
        )
        
        # Fire the conversational execution turn
        response = await framework_runner.run_turn(prompt)
        return response.text