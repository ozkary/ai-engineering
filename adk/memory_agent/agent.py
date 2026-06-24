import os
from tools.session import PersistentSessionManager, SessionConfig
from tool_agent.agent import ToolAgent


class MemoryAgent(ToolAgent):
    """
    Layer 3: Combines identity, custom toolsets, and persistent memory
    stores (e.g., SQLite, local JSON, or a vector store) to maintain
    continuity across sessions.
    """

    def __init__(self):
        super().__init__()
        user_prompt = os.getenv("USER_PROMPT", "")
        if user_prompt:
            # Append local task context to the inherited system instruction string
            self.instruction += f"\n\n {user_prompt}"

        self.agent = self.build_agent()

    async def setup_session_context(
        self, app_name: str, user_id: str, session_id: str
    ) -> PersistentSessionManager:
        """
        Leverages our core session manager to attach a persistent
        SQLite footprint to this agent configuration.
        """
        config = SessionConfig(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            db_path=os.getenv("SESSION_DB_PATH", "data/memory_agent.db"),
        )

        manager = PersistentSessionManager(config)
        await manager.hydrate_session()
        return manager


# Instance for CLI discovery inside tool_agent/ package boundary
memory_agent = MemoryAgent().agent
root_agent = MemoryAgent().agent
