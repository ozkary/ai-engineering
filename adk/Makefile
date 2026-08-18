.PHONY: setup dev test run-mcp run-agent clean prompts run-dark-stage1 run-dark-stage2 run-dark-stage3

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
	uv run pytest || [ $$? -eq 5 ]




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

# Launch the dark agent sandbox
run-dark:
	clear
	uv run adk web dark_agent/

run-main:
	uv run python3 main.py

run-dark-stage1:
	uv run python3 dark_agent_main.py --stage 1

run-dark-stage2:
	uv run python3 dark_agent_main.py --stage 2

run-dark-stage3:
	uv run python3 dark_agent_main.py --stage 3

prompts:
	@echo "🔒 [BUILD] Compiling cryptographic signatures for prompt templates..."
	@python3 -c "import sys, os, hmac, hashlib; sys.path.insert(0, os.getcwd()); from security.secure_auth import VaultSecretManager; src = 'prompts/tool_agent_instructions.md'; sig = 'prompts/tool_agent_instructions.signed.md'; sm = VaultSecretManager(); key = sm.get_secret('ozkary_agent_secret').encode('utf-8'); data = open(src, 'rb').read() if os.path.exists(src) else b''; h = hmac.new(key, data, hashlib.sha256).hexdigest() if data else ''; open(sig, 'w').write(h) if h else None; print(f'✅ Generated HMAC prompt signature: {sig} ({h})') if h else None"


run-check-types:
	uv run python3 -c "import google.adk.utils; print(dir(google.adk.utils))"