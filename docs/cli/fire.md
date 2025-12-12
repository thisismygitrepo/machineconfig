# fire

Python Fire-based job execution system for running scripts and functions directly from the command line.

---

## Usage

```bash
fire [PATH] [FUNCTION] [OPTIONS] [ARGS]...
```

---

## Overview

The `fire` command provides a flexible interface for executing Python scripts and functions directly from the command line. Built on top of [Python Fire](https://github.com/google/python-fire), it extends the standard functionality with:

- **Multiple execution modes**: Interactive (IPython), debug (pudb/ipdb), module, and script modes
- **Notebook integration**: Convert and run scripts in Jupyter, Marimo, or Streamlit
- **Remote execution**: Run on remote machines or submit to cloud compute
- **Development tools**: File watching, git integration, and virtual environment support
- **Terminal multiplexing**: Run in background Zellij tabs

---

## Quick Start

```bash
# Run main module
fire script.py

# Run specific function
fire script.py my_function

# Run with arguments
fire script.py process --input data.csv --output result.json

# Choose function interactively (with fuzzy search)
fire script.py -c
```

---

## Command Reference

### Arguments

| Argument | Description |
|----------|-------------|
| `PATH` | Path to Python file, shell script, or executable (default: `.`) |
| `FUNCTION` | Function name to execute (optional) |

### Execution Modes

| Option | Short | Description |
|--------|-------|-------------|
| `--script` | `-s` | Launch as a plain Python script (without Fire) |
| `--module` | `-m` | Launch as a Python module (`python -m`) |
| `--interactive` | `-i` | Run interactively using IPython with your profile |
| `--debug` | `-d` | Enable debug mode (pudb on Linux/Mac, ipdb on Windows) |
| `--optimized` | `-O` | Run with Python optimizations (`python -OO`) |
| `--choose-function` | `-c` | Interactively choose a function using fuzzy finder |

### Virtual Environment

| Option | Short | Description |
|--------|-------|-------------|
| `--ve` | `-v` | Specify virtual environment name to use |

### Notebook & Web Apps

| Option | Short | Description |
|--------|-------|-------------|
| `--jupyter` | `-j` | Open script in Jupyter Lab |
| `--marimo` | `-M` | Convert and open in Marimo notebook |
| `--streamlit` | `-S` | Run as Streamlit web app with QR code display |
| `--environment` | `-E` | Server binding: `ip`, `localhost`, `hostname`, or custom URL |

### Remote & Background Execution

| Option | Short | Description |
|--------|-------|-------------|
| `--remote` | `-r` | Launch on a remote machine |
| `--submit-to-cloud` | `-C` | Submit job to cloud compute |
| `--zellij-tab` | `-z` | Run in a new Zellij tab with given name |
| `--cmd` | `-B` | Create a cmd fire command for async launch (Windows) |

### Development Tools

| Option | Short | Description |
|--------|-------|-------------|
| `--watch` | `-w` | Watch file for changes and auto-restart (uses watchexec) |
| `--loop` | `-l` | Infinite loop - restart after completion or interruption |
| `--git-pull` | `-g` | Pull git repository before running |

### Path Management

| Option | Short | Description |
|--------|-------|-------------|
| `--holdDirectory` | `-D` | Stay in current directory (don't cd to script location) |
| `--PathExport` | `-P` | Add repository root to `PYTHONPATH` |

---

## Supported File Types

| Extension | Behavior |
|-----------|----------|
| `.py` | Python scripts - can run as Fire, module, or script |
| `.sh` | Shell scripts - source directly |
| `.ps1` | PowerShell scripts - source directly |
| (none) | Executables - run directly |

---

## Examples

### Basic Execution

```bash
# Run the main module (equivalent to `python -m fire script.py`)
fire script.py

# Run a specific function
fire my_jobs.py cleanup

# Run function with keyword arguments
fire my_jobs.py cleanup --days 30 --dry-run

# Run function with positional arguments
fire my_jobs.py process data.csv result.json
```

### Interactive Function Selection

When you have a file with multiple functions, use `-c` to get an interactive fuzzy finder:

```bash
fire utils.py -c
```

This parses the file, extracts all functions with their docstrings and arguments, and presents them for selection. If the selected function has parameters without defaults, you'll be prompted to enter values.

### Debug Mode

```bash
# Debug with pudb (Linux/Mac) or ipdb (Windows)
fire buggy_script.py -d

# Debug a specific function interactively
fire utils.py -c -d
```

When combining `-c` (choose function) with `-d` (debug), fire creates a temporary script that imports your module and calls the selected function, then launches the debugger on that script.

### IPython Interactive Mode

```bash
# Launch in IPython with your profile
fire utils.py -i

# Useful for exploring modules interactively
fire data_utils.py -i
```

This uses your IPython profile from the virtual environment if available.

### Notebook Integration

#### Marimo

```bash
# Convert Python script to Marimo notebook and open
fire analysis.py -M
```

The script is converted to a Marimo notebook in a temporary directory and opened with `marimo edit`.

#### Jupyter

```bash
# Open in Jupyter Lab
fire analysis.py -j
```

#### Streamlit

```bash
# Run as Streamlit app
fire dashboard.py -S

# Specify server binding
fire dashboard.py -S -E localhost
fire dashboard.py -S -E ip        # Use LAN IP
fire dashboard.py -S -E hostname  # Use machine hostname
fire dashboard.py -S -E myserver.example.com
```

Streamlit mode automatically:

- Detects `.streamlit/config.toml` configuration
- Displays QR codes for easy mobile access
- Shows URLs for LAN IP, hostname, and localhost

### Background & Parallel Execution

#### Zellij Tab

```bash
# Run in a new Zellij tab named "DataSync"
fire sync_job.py -z "DataSync"

# Long-running process in background
fire monitor.py check -z "Monitor" -l
```

#### Loop Mode

```bash
# Restart script after completion (useful for daemons)
fire watcher.py -l

# Combined with watch for development
fire server.py run -l
```

### Development Workflow

```bash
# Watch for changes and auto-restart
fire server.py run -w

# Pull latest code before running
fire deploy.py release -g

# Export repo root to PYTHONPATH for imports
fire nested/deep/script.py -P
```

### Module Mode

```bash
# Run as Python module (useful for packages)
fire src/mypackage/cli.py -m

# This translates to: python -m mypackage.cli
```

### Virtual Environments

```bash
# Use a specific virtual environment
fire analysis.py process -v myenv

# All execution happens via `uv run --project`
```

### Cloud Submission

```bash
# Submit to cloud compute
fire heavy_compute.py train -C

# This uses machineconfig's cloud job submission system
```

---

## Writing Fire-Compatible Scripts

### Basic Function

```python
# jobs.py

def greet(name: str, greeting: str = "Hello"):
    """Greet someone.
    
    Args:
        name: Person's name
        greeting: Greeting phrase
    """
    print(f"{greeting}, {name}!")
```

```bash
fire jobs.py greet --name Alice
# Output: Hello, Alice!

fire jobs.py greet --name Bob --greeting "Welcome"
# Output: Welcome, Bob!
```

### Multiple Functions

```python
# data_jobs.py

def download(url: str, output: str = "data.csv"):
    """Download data from URL."""
    import httpx
    response = httpx.get(url)
    Path(output).write_bytes(response.content)
    print(f"Downloaded to {output}")

def process(input_file: str, output_file: str, format: str = "csv"):
    """Process data file.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        format: Output format (csv, json, parquet)
    """
    import polars as pl
    df = pl.read_csv(input_file)
    # ... processing ...
    getattr(df, f"write_{format}")(output_file)

def cleanup(days: int = 7, dry_run: bool = False):
    """Clean up old files.
    
    Args:
        days: Delete files older than this many days
        dry_run: Preview without deleting
    """
    from pathlib import Path
    import time
    
    cutoff = time.time() - (days * 86400)
    for f in Path("/tmp").iterdir():
        if f.stat().st_mtime < cutoff:
            if dry_run:
                print(f"Would delete: {f}")
            else:
                f.unlink()
```

```bash
# Run specific functions
fire data_jobs.py download --url "https://example.com/data.csv"
fire data_jobs.py process data.csv output.json --format json
fire data_jobs.py cleanup --days 14 --dry-run

# Choose interactively
fire data_jobs.py -c
```

### Script with Main Block

```python
# analysis.py
"""Data analysis script for quarterly reports."""

import polars as pl

def load_data():
    return pl.read_csv("data.csv")

def analyze():
    df = load_data()
    print(df.describe())

if __name__ == "__main__":
    analyze()
```

```bash
# Run as main (executes __main__ block)
fire analysis.py

# Or select specific function
fire analysis.py analyze
fire analysis.py -c  # Shows "RUN AS MAIN" option plus all functions
```

---

## How It Works

1. **Path Resolution**: Resolves the given path and detects the repository root
2. **Command Building**: Constructs the appropriate `uv run` command based on options
3. **Execution**: Launches the script via shell with all modifiers applied

The command uses `uv run --project <repo_root>` to ensure proper dependency resolution from `pyproject.toml`.

---

## Tips & Best Practices

### Docstrings Matter

Write good docstrings - they appear in the interactive function chooser:

```python
def my_function(arg1: str, arg2: int = 10):
    """Short description shown in chooser.
    
    Longer description with details.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    """
```

### Type Hints for Argument Parsing

Fire uses type hints to convert command-line strings:

```python
def process(count: int, ratio: float, enabled: bool = True):
    ...
```

```bash
fire script.py process --count 5 --ratio 0.5 --enabled false
```

### Combining Options

Options can be combined for powerful workflows:

```bash
# Debug with git pull and path export
fire feature.py test -d -g -P

# Watch in loop with specific environment
fire server.py run -w -l -E localhost
```

---

## See Also

- [Python Fire Documentation](https://github.com/google/python-fire)
- [Marimo](https://marimo.io/) - Reactive Python notebooks
- [Streamlit](https://streamlit.io/) - Python web apps
- [watchexec](https://github.com/watchexec/watchexec) - File watcher used by `--watch`
- [pudb](https://documen.tician.de/pudb/) - Python debugger used by `--debug`
