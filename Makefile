.PHONY: setup dev test run-mcp run-agent clean

# run virtual environment
# uv run adk web agent_folder

# make setup: Instantly pins Python 3.12 and sets up your entire high-performance local .venv.
# make test: Runs your Gherkin integration specs via behave and unit tests via pytest simultaneously.
# make run-mcp: Spins up your localized ML inference server so your agents can hook into it.
# make dev: Launches your Antigravity command line session.

# 1. Initialize and synchronize the entire Rust-backed environment
setup:
	uv python pin 3.12
	uv sync

# Run static analysis and linting checks
lint:
	uv run ruff check adk/
	uv run ruff format --check adk/

# Auto-fix linting issues cleanly
format:
	uv run ruff check --fix adk/
	uv run ruff format adk/

# 2. Run your Spec-Driven/BDD tests using Gherkin files
test:
	uv run behave specs/features/
	uv run pytest

# 3. Fire up your custom Heart Disease ML Model as an isolated MCP Server
run-mcp:
	uv run uvicorn src.mcp_server:app --reload --port 8000

# 4. Boot up the Antigravity CLI workspace
dev:
	agy

# 5. Clean up temporary Python and cache artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".behave_cache" -exec rm -rf {} +

