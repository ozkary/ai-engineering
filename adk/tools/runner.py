# tools/runner.py

class AgentRunner:
    """
    Lazy initialization proxy for AgentRunner to prevent circular imports
    during packages startup (tools package imports tools.runner which imports core.runner).
    """
    def __new__(cls, *args, **kwargs):
        from core.runner import AgentRunner as RealAgentRunner
        return RealAgentRunner(*args, **kwargs)
