import os
from tools.session import PersistentSessionManager, SessionConfig


# graph
from tool_agent.agent import ToolAgent


class MemoryAgent(ToolAgent):
    """
    Layer 3: Combines identity, custom toolsets, and persistent memory
    stores (e.g., SQLite, local JSON, or a vector store) to maintain
    continuity across sessions.
    """

    def __init__(self):
        super().__init__()

        # Configure your storage layer properties here (e.g., database file paths)
        self.storage_path = "data/memory_store.db"

        # 3. Bind persistence layers to the agent
        self.initialize_persistence()

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
