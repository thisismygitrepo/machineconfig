# Code Style

Guidelines for writing code that fits the Machineconfig codebase.

---

## Formatting

We use [Ruff](https://docs.astral.sh/ruff/) for formatting and linting.

### Format Code

```bash
uv run ruff format src/
```

### Check Linting

```bash
uv run ruff check src/
```

---

## Type Hints

All code should include type hints:

```python
def process_file(path: str, encoding: str = "utf-8") -> list[str]:
    """Process a file and return lines."""
    ...
```

Run type checking with:

```bash
uv run pyright
```

---

## Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of function.
    
    Longer description if needed, explaining what the function
    does in more detail.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When param2 is negative.
        
    Example:
        >>> example_function("test", 42)
        True
    """
    ...
```

---

## Imports

Organize imports in this order:

1. Standard library
2. Third-party packages
3. Local imports

```python
import os
from pathlib import Path

import rich
from rich.console import Console

from machineconfig.utils import accessories
```

---

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Functions | snake_case | `process_file()` |
| Variables | snake_case | `file_path` |
| Classes | PascalCase | `RemoteMachine` |
| Constants | UPPER_SNAKE | `DEFAULT_TIMEOUT` |
| Modules | snake_case | `remote_machine.py` |

---

## Error Handling

Use specific exceptions and provide helpful messages:

```python
def connect(host: str) -> Connection:
    if not host:
        raise ValueError("Host cannot be empty")
    
    try:
        return Connection(host)
    except ConnectionError as e:
        raise ConnectionError(f"Failed to connect to {host}: {e}") from e
```

---

## Pre-commit Hooks

Pre-commit runs automatically on commit:

```yaml
# Runs ruff formatting
# Runs ruff linting
# Checks for trailing whitespace
# Validates YAML
```

To run manually:

```bash
uv run pre-commit run --all-files
```
