# Development Setup

Set up your local development environment for contributing to Machineconfig.

---

## Prerequisites

- Python 3.13+
- [UV](https://docs.astral.sh/uv/) (recommended)
- Git

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/thisismygitrepo/machineconfig.git
cd machineconfig
```

### 2. Install Dependencies

```bash
uv sync --group dev
```

This installs all development dependencies.

### 3. Install Pre-commit Hooks

```bash
uv run pre-commit install
```

---

## Development Workflow

### Running Tests

```bash
uv run pytest
```

### Type Checking

```bash
uv run pyright
# or
uv run mypy src/
```

### Linting

```bash
uv run ruff check src/
uv run ruff format src/
```

### Building Documentation

```bash
uv run mkdocs serve
```

Visit `http://127.0.0.1:8000` to preview docs.

---

## Project Structure

```
machineconfig/
├── src/machineconfig/    # Main package
│   ├── cluster/          # Remote operations
│   ├── jobs/             # Job execution
│   ├── scripts/          # CLI implementations
│   ├── settings/         # Config templates
│   └── utils/            # Utilities
├── docs/                 # Documentation
├── tests/                # Test suite
└── pyproject.toml        # Project config
```

---

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes

3. Run tests and linting:
   ```bash
   uv run pytest
   uv run ruff check src/
   ```

4. Commit with clear messages:
   ```bash
   git commit -m "Add feature: description"
   ```

5. Push and open a PR

---

## Building the Package

```bash
uv build
```

This creates distribution files in `dist/`.
