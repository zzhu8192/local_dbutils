# Repository Guidelines

## Project Structure & Module Organization
- Source lives in `src/dbutils/` (package: `dbutils`).
- Tests in `tests/` mirroring package layout (e.g., `tests/connections/test_pool.py`).
- Examples and scripts in `examples/` and `scripts/`.
- Optional assets/fixtures in `tests/fixtures/`.

Suggested modules: `connections/`, `adapters/`, `migrations/`, `utils/`.

## Build, Test, and Development Commands
- `make setup` — create virtualenv and install deps (dev + test).
- `make lint` — run static checks (ruff/flake8, isort).
- `make format` — auto-format (black + isort).
- `make type` — type-check (mypy/pyright).
- `make test` — run tests with coverage (pytest).
- `make build` — build distributable (wheel + sdist).

If `make` is unavailable, equivalents:
- `pip install -e .[dev,test]`
- `pytest -q` and `coverage run -m pytest`

## Coding Style & Naming Conventions
- Python 3.10+; 4-space indent; UTF-8.
- Naming: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Imports: standard → third-party → local (use isort).
- Formatting: black; Linting: ruff/flake8; Type hints required for public APIs.
- Docstrings: concise, Google-style; include examples for DB connections.

## Testing Guidelines
- Framework: pytest with `tests/test_*.py` discovery.
- Unit tests isolate DB by default (use fakes/SQLite in-memory). Mark real-DB tests as `@pytest.mark.integration`.
- Aim for ≥90% coverage on core modules; run `make test` locally before PRs.
- Use fixtures in `tests/fixtures/` for sample schemas and data.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`, `ci:`.
- Keep commits focused; subject ≤50 chars; include rationale in body when helpful.
- PRs must: describe change, link issues, note breaking changes, update docs/tests, and show local test results.

## Security & Configuration Tips
- Never commit secrets; provide `.env.example` and use `DATABASE_URL`/`DBUTILS_*` vars.
- Always parameterize SQL; avoid string interpolation in queries.
- Sanitize logs; redact credentials in errors.

## Agent-Specific Instructions
- Follow this guide when editing; do not alter unrelated files.
- Prefer `rg` for search, keep patches minimal, and mirror test layout when adding modules.
