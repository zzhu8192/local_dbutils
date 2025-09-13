.PHONY: build clean deploy run

build:
	uv sync
	uv build --refresh --wheel

clean:
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "Deactivating virtual environment..."; \
		deactivate 2>/dev/null || true; \
	fi
	@if [ -d ".venv" ]; then \
		echo "Cleaning uv cache and dependencies..."; \
		uv clean; \
	fi
	@echo "Removing build artifacts..."
	@rm -rf dist/ *.egg-info/ uv.lock .venv/ build/

test:
	uv pip install --group test 
	uv run pytest -v
