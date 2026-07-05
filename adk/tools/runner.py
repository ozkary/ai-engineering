# core/runner.py
from google.adk import Runner
from tools.session import PersistentSessionManager, SessionConfig
# from google.adk.events.event import types


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

        print(
            f"[AgentRunner] Initializing ADK loop for agent: '{agent_instance.name}'..."
        )

        # Updated to match your explicit framework injection contract
        runner = Runner(
            agent=agent_instance,
            app_name=self.config.app_name,
            session_service=self.session_context,
        )

        # Standard ADK message wrapping
        content = {
            "role": "user",
            "parts": [{"text": prompt}]
        }
        # content = types.Content(role='user', parts=[types.Part(text=prompt)])

        # Fire the conversational execution turn        
        events = runner.run_async(
            user_id = self.config.user_id,
            session_id = self.config.session_id,
            new_message = content
        )
        final_response = ""
        async for event in events:          
            if event.is_final_response():
                for part in event.content.parts:
                        if part.text:
                            final_response += part.text
                
        # Identify the specific agent speaking in the console
        print(f"[{agent_instance.name}]: {final_response}")
        
        return final_response
