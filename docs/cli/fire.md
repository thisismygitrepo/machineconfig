# fire

Python Fire-based job execution system for running scripts and functions.

---

## Usage

```bash
fire [PATH] [FUNCTION] [OPTIONS] [ARGS]...
```

---

## Overview

The `fire` command provides a flexible interface for executing Python scripts and functions directly from the command line, with support for various execution modes including interactive, debug, remote, and notebook environments.

---

## Basic Usage

### Run a Script

```bash
# Run main function from script
fire script.py

# Run specific function
fire script.py my_function

# Run with arguments (passed to the function via Fire)
fire script.py process --input data.csv --output result.json
```

### Interactive Selection

```bash
# Choose function interactively
fire script.py --choose-function

# Or use shortcut
fire script.py -c
```

---

## Execution Options

| Option | Short | Description |
|--------|-------|-------------|
| `--ve` | `-v` | Virtual environment name |
| `--cmd` | `-B` | Create a cmd fire command for async launch |
| `--interactive` | `-i` | Run interactively using IPython |
| `--debug` | `-d` | Enable debug mode |
| `--choose-function` | `-c` | Choose function interactively |
| `--loop` | `-l` | Infinite loop (restart after completion) |
| `--script` | `-s` | Launch as script without Fire |
| `--module` | `-m` | Launch as Python module |
| `--optimized` | `-O` | Run with Python optimizations |
| `--watch` | `-w` | Watch file for changes |
| `--git-pull` | `-g` | Pull git repo before running |
| `--holdDirectory` | `-D` | Don't cd to script directory |
| `--PathExport` | `-P` | Add repo root to PYTHONPATH |

---

## Notebook Modes

| Option | Short | Description |
|--------|-------|-------------|
| `--jupyter` | `-j` | Open in Jupyter notebook |
| `--marimo` | `-M` | Open in Marimo notebook |
| `--streamlit` | `-S` | Run as Streamlit app |

**Examples:**

```bash
# Open in Jupyter
fire analysis.py --jupyter

# Open in Marimo
fire dashboard.py --marimo

# Run as Streamlit app
fire app.py --streamlit
```

---

## Remote Execution

| Option | Short | Description |
|--------|-------|-------------|
| `--remote` | `-r` | Launch on remote machine |
| `--submit-to-cloud` | `-C` | Submit to cloud compute |
| `--zellij-tab` | `-z` | Open in new Zellij tab |
| `--environment` | `-E` | Choose ip/localhost/hostname/url |

**Examples:**

```bash
# Run in new Zellij tab
fire long_task.py -z "Background Task"

# Submit to remote
fire heavy_compute.py --remote
```

---

## Examples

### Basic Execution

```bash
# Run a function with arguments
fire my_jobs.py cleanup --days 30

# Run with virtual environment
fire analysis.py process --ve myenv

# Debug mode
fire buggy_script.py -d
```

### Development Workflow

```bash
# Watch for changes and re-run
fire server.py run --watch

# Interactive mode for testing
fire utils.py --interactive

# Pull latest and run
fire deploy.py release --git-pull
```

### Notebooks

```bash
# Data analysis in Jupyter
fire analysis.py --jupyter

# Interactive dashboard in Marimo
fire dashboard.py --marimo

# Web app with Streamlit
fire app.py --streamlit --environment localhost
```

### Background Tasks

```bash
# Run in loop (restarts on completion/error)
fire monitor.py check --loop

# Run in separate Zellij tab
fire backup.py full -z "Backup"

# Create async launch command
fire long_process.py compute --cmd
```

---

## Creating Jobs

Jobs are regular Python functions:

```python
# my_jobs.py

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

def process_data(input_file: str, output_file: str, format: str = "csv"):
    """Process data file.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        format: Output format (csv, json, parquet)
    """
    import polars as pl
    
    df = pl.read_csv(input_file)
    # ... processing ...
    if format == "json":
        df.write_json(output_file)
    else:
        df.write_csv(output_file)
```

Then run them:

```bash
fire my_jobs.py cleanup --days 14
fire my_jobs.py cleanup --days 7 --dry-run
fire my_jobs.py process_data data.csv result.json --format json
```
