# core/session.py
import os
from dataclasses import dataclass, field
from google.adk.sessions import SqliteSessionService  
# from google.adk.sessions import InMemorySessionService

@dataclass
class SessionConfig:
    """Data blueprint for initializing an agent session state."""
    app_name: str
    user_id: str
    session_id: str
    initial_state: dict = field(default_factory=dict)
    db_path: str = "data/agent_session_memory.db"

class PersistentSessionManager:
    """
    Manages the lifecycle of file-backed SQLite session stores.
    Handles automatic database initialization and session hydration.
    """
    def __init__(self, config: SessionConfig):
        self.config = config
        
        # Ensure the directory path exists before SQLite initializes
        db_dir = os.path.dirname(self.config.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        # 1. Initialize the explicit file-backed SQLite service
        print(f"🗄️ [Session] Binding persistence engine to disk file: {self.config.db_path}")
        self.service = SqliteSessionService(database_path=self.config.db_path)

    async def hydrate_session(self) -> SqliteSessionService:
        """
        Creates or resumes the session sequence on disk. 
        If the database file doesn't exist, SQLite writes it automatically.
        """
        print(f"🔄 [Session] Hydrating session ID: '{self.config.session_id}' for User: '{self.config.user_id}'")
        
        await self.service.create_session(
            app_name=self.config.app_name,
            user_id=self.config.user_id,
            session_id=self.config.session_id,
            state=self.config.initial_state
        )
        
        return self.service