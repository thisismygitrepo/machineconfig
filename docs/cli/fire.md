# fire

Fire-based job execution system.

---

## Usage

```bash
fire [OPTIONS] COMMAND [ARGS]...
```

---

## Overview

The `fire` command provides a Python Fire-based interface for executing jobs and functions directly from the command line.

---

## Running Jobs

### Basic Execution

```bash
fire run MODULE.FUNCTION [ARGS]
```

**Example:**

```bash
fire run my_module.my_function --arg1 value1 --arg2 value2
```

---

### With Positional Arguments

```bash
fire run process_data input.csv output.csv --format json
```

---

## Job Discovery

### List Available Jobs

```bash
fire list [MODULE]
```

Lists all callable functions in a module.

---

### Job Information

```bash
fire info MODULE.FUNCTION
```

Shows function signature, docstring, and parameters.

---

## Execution Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show detailed output |
| `--dry-run` | Preview without execution |
| `--timeout` | Set execution timeout |
| `--background` | Run in background |

---

## Interactive Mode

Start an interactive session:

```bash
fire interactive MODULE
```

This opens a REPL with the module's functions available.

---

## Examples

```bash
# Run a function
fire run my_jobs.cleanup --days 30

# List functions in module
fire list my_jobs

# Get function info
fire info my_jobs.process_data

# Run with timeout
fire run long_task.compute --timeout 3600

# Run in background
fire run backup.full --background
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
    # Implementation
    pass

def process_data(input_file: str, output_file: str, format: str = "csv"):
    """Process data file.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        format: Output format (csv, json, parquet)
    """
    # Implementation
    pass
```

Then run them:

```bash
fire run my_jobs.cleanup --days 14
fire run my_jobs.process_data data.csv result.json --format json
```
