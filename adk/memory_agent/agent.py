import os
# from tools.session import PersistentSessionManager, SessionConfig
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

        if self.agent is None:
            self.agent = self.build_agent()

    async def execute_task(self, message: str, session_context=None):
        """
        Executes a reasoning loop, passing along whatever session context 
        the runner provided.
        """
        return await self.agent.run_async(
            message=message,
            context=session_context  # Completely injected from the outside
        )
  

# Instance for CLI discovery inside tool_agent/ package boundary
memory_agent = MemoryAgent().agent
root_agent = memory_agent