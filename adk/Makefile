.PHONY: setup dev test run-mcp run-agent clean

# run virtual environment
# uv run adk web agent_folder

# make setup: Instantly pins Python 3.12 and sets up your entire high-performance local .venv.
# make test: Runs your Gherkin integration specs via behave and unit tests via pytest simultaneously.

# 1. Initialize and synchronize the entire Rust-backed environment
setup:
	uv python pin 3.12
	uv sync

# Run static analysis and linting checks
lint:
	uv run ruff check ./
	uv run ruff format --check ./

# Auto-fix linting issues cleanly
format:
	uv run ruff check --fix ./
	uv run ruff format ./

# 2. Run your Spec-Driven/BDD tests using Gherkin files
test:
	uv run behave specs/features/
	uv run pytest

# 5. Clean up temporary Python and cache artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".behave_cache" -exec rm -rf {} +

# Launch the basic agent sandbox
run-basic:
	clear
	uv run adk web basic_agent/

# Launch the tool-equipped agent sandbox
run-tool:
	clear
	uv run adk web tool_agent/

# Launch the memory agent sandbox
run-memory:
	clear
	uv run adk web memory_agent/
