import os
from datetime import datetime
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
        if not self.session_context:
            manager = PersistentSessionManager(self.config)
            self.session_context = await manager.hydrate_session()

        print(
            f"[AgentRunner] Initializing ADK loop for agent: '{agent_instance.name}'..."
        )

        runner = Runner(
            agent=agent_instance,
            app_name=self.config.app_name,
            session_service=self.session_context,
        )

        from google.genai.types import Content, Part
        content = Content(
            role="user",
            parts=[Part(text=prompt)]
        )

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
                
        print(f"[{agent_instance.name}]: {final_response}")
        return final_response

def initialize_runner(app_name: str, user_id: str = "ozkary") -> AgentRunner:
    """Initializes the persistent session database runner configuration."""
    print(f"🔧 [Workflow] Initializing persistent AgentRunner session context for app '{app_name}'...")
    core_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(core_dir)
    absolute_db_path = os.path.join(project_root, "data", "mta_pipeline_memory.db")
    db_connection_uri = f"sqlite+aiosqlite:///{absolute_db_path}"

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    pipeline_config = SessionConfig(
        app_name=app_name,
        user_id=user_id,
        session_id=f"demo_{session_id}",
        db_path=db_connection_uri,
    )
    return AgentRunner(config=pipeline_config)
