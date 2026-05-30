.PHONY: help run lock clean

# Default goal
.DEFAULT_GOAL := run

help:
	@echo "======================================================================"
	@echo "                  Streamlit & LangChain Boilerplate                   "
	@echo "======================================================================"
	@echo "Available commands:"
	@echo "  make run        - Install 'uv' (if missing), sync dependencies, setup .env,"
	@echo "                    and launch the Streamlit application."
	@echo "  make lock       - Re-generate the uv lockfile (uv.lock)."
	@echo "  make clean      - Clean cache files (.pytest_cache, __pycache__, etc.)"
	@echo "======================================================================"

run:
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp .env.example .env; \
	fi
	@which uv >/dev/null 2>&1 || (echo "Installing 'uv' package manager..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
	@export PATH="$$HOME/.local/bin:$$PATH" && uv sync && echo "Starting Streamlit App..." && uv run streamlit run "app/🏥_Clinical_Hub.py" --server.port=8080

lock:
	@export PATH="$$HOME/.local/bin:$$PATH" && uv lock

clean:
	@echo "Cleaning up temp and cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".streamlit" ! -name "config.toml" ! -name "secrets.toml" -exec rm -rf {} +
	@echo "Clean completed."