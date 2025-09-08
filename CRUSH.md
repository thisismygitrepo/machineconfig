# CRUSH.md: Guidelines for Agentic Coding in machineconfig

## Build Commands
- Install dependencies: `uv sync`
- Build package: `uv build`
- Install editable: `uv pip install -e .`
- Generate docs: `make docs` (requires `pip install .[docs]` first)

## Lint and Typecheck Commands
- Lint and typecheck all: `./scripts/lint_and_type_check.sh` (outputs to .linters/*.md)
- Single file lint: `uv run pylint file.py`
- Single file typecheck: `uv run pyright file.py`
- Fix issues: Review .linters/ outputs and edit accordingly

## Test Commands
- Run all tests: `uv run pytest` (assuming pytest; install with `uv add pytest --dev` if needed)
- Run single test: `uv run pytest tests/test_file.py::test_function`
- Run with coverage: `uv run coverage run -m pytest; uv run coverage report`

## Code Style Guidelines
- Use Python 3.13+; prefer functional style over OOP
- Type hints: Fully qualified (e.g., dict[str, int]); return types mandatory; use TypedDict/dataclasses/Literals
- Imports: Absolute preferred; no dangling/unused (prefix _)
- Formatting: ~150 chars/line; triple-quoted f-strings; no default args; avoid comments/docstrings unless necessary
- Error handling: Explicit, rigorous; use pathlib.Path; prefer polars over pandas
- Temp files: Place in .ai/tmp_scripts/
- Never edit pyproject.toml manually; use uv add/remove
- After edits: Run lint/typecheck on touched files; fix issues

## AI-Specific Rules (from Cursor/Copilot)
- Install uv if missing: See https://github.com/astral-sh/uv
- Run scripts: `uv run file.py`
- Modern syntax: 3.13 features, no outdated styles
- Linters respect configs in repo/home; use # type: ignore only when necessary