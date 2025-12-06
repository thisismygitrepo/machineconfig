# Automation

Automate repetitive tasks and workflows with machineconfig.

---

## Overview

Machineconfig provides automation capabilities for:

- Script execution and job management
- Session-based task orchestration
- Multi-process parallel execution
- Remote machine operations

---

## Fire Jobs

Execute Python scripts and functions using the Fire-based interface:

```bash
fire script.py function_name --arg1 value1
```

### Job Definition

Jobs are Python functions that can be executed directly:

```python
# my_jobs.py

def backup_data(source: str, destination: str, compress: bool = True):
    """Backup data to destination."""
    import shutil
    from pathlib import Path
    
    src = Path(source)
    dst = Path(destination)
    
    if compress:
        shutil.make_archive(str(dst), 'zip', str(src))
    else:
        shutil.copytree(src, dst)
    
    print(f"Backed up {source} to {destination}")

def cleanup_old_files(directory: str, days: int = 30, dry_run: bool = False):
    """Remove files older than specified days."""
    from pathlib import Path
    import time
    
    cutoff = time.time() - (days * 86400)
    path = Path(directory)
    
    for f in path.rglob("*"):
        if f.is_file() and f.stat().st_mtime < cutoff:
            if dry_run:
                print(f"Would delete: {f}")
            else:
                f.unlink()
                print(f"Deleted: {f}")
```

### Running Jobs

```bash
# With default parameters
fire my_jobs.py backup_data ~/data ~/backups/data

# With custom parameters
fire my_jobs.py cleanup_old_files /tmp --days 7

# Preview with dry run
fire my_jobs.py cleanup_old_files /tmp --days 7 --dry-run
```

### Advanced Execution

```bash
# Watch for changes and re-run
fire my_jobs.py monitor --watch

# Run in debug mode
fire my_jobs.py process -d

# Run in loop (auto-restart)
fire my_jobs.py daemon --loop

# Open in Zellij tab
fire my_jobs.py long_task -z "Background"
```

---

## Session-Based Automation

Use layout files to orchestrate multiple tasks:

### Create a Layout

```bash
sessions create-template automation_tasks -t 4
```

This creates a template layout file:

```json
[
  {
    "layoutName": "automation_tasks",
    "tabs": [
      {"tabName": "task1", "command": ""},
      {"tabName": "task2", "command": ""},
      {"tabName": "task3", "command": ""},
      {"tabName": "task4", "command": ""}
    ]
  }
]
```

### Define Your Workflow

Edit the layout file with your commands:

```json
[
  {
    "layoutName": "daily_automation",
    "tabs": [
      {
        "tabName": "backup",
        "command": "fire backup.py run_backup ~/data"
      },
      {
        "tabName": "sync",
        "command": "rclone sync ~/documents remote:documents"
      },
      {
        "tabName": "cleanup",
        "command": "fire maintenance.py cleanup_temp"
      },
      {
        "tabName": "monitor",
        "command": "btop"
      }
    ]
  }
]
```

### Run the Workflow

```bash
# Run all tasks
sessions run daily_automation.json

# Run with monitoring
sessions run daily_automation.json --monitor

# Kill sessions when all tasks complete
sessions run daily_automation.json --monitor --kill-upon-completion
```

---

## Multi-Process Execution

Run a function across multiple parallel processes:

```bash
# Create layout for 8 parallel workers
sessions create-from-function -n 8 -p ./worker.py -f process_chunk
```

### Example: Parallel Data Processing

```python
# worker.py
import os

def process_chunk(chunk_id: int = 0, total_chunks: int = 8):
    """Process a chunk of data.
    
    Args:
        chunk_id: This worker's chunk ID (0 to total_chunks-1)
        total_chunks: Total number of parallel workers
    """
    # Get list of files to process
    files = list(Path("data").glob("*.csv"))
    
    # Calculate this worker's slice
    chunk_size = len(files) // total_chunks
    start = chunk_id * chunk_size
    end = start + chunk_size if chunk_id < total_chunks - 1 else len(files)
    
    my_files = files[start:end]
    
    for f in my_files:
        # Process file
        print(f"Worker {chunk_id}: Processing {f}")
        # ... processing logic ...
```

---

## DevOps Scripts

Execute predefined scripts from the devops command:

```bash
# List available scripts
devops execute --list

# Run a script
devops execute my_automation_script

# Interactive selection
devops execute -i
```

### Script Locations

Scripts can be placed in various locations:

| Location | Flag | Description |
|----------|------|-------------|
| Private | `-w private` | Personal automation scripts |
| Public | `-w public` | Shared scripts |
| Library | `-w library` | Package scripts |
| Dynamic | `-w dynamic` | Generated scripts |
| Custom | `-w custom` | Custom location |

---

## Integration Examples

### CI/CD Pipeline Script

```python
# deploy.py

def build():
    """Build the application."""
    import subprocess
    subprocess.run(["uv", "build"], check=True)
    print("Build complete")

def test():
    """Run test suite."""
    import subprocess
    result = subprocess.run(["pytest", "-v"])
    if result.returncode != 0:
        raise SystemExit("Tests failed")
    print("Tests passed")

def deploy(environment: str = "staging"):
    """Deploy to specified environment."""
    import subprocess
    
    if environment == "production":
        print("Deploying to production...")
        # Production deployment logic
    else:
        print(f"Deploying to {environment}...")
        # Staging deployment logic
    
    print(f"Deployed to {environment}")

def release(skip_tests: bool = False):
    """Full release pipeline."""
    build()
    if not skip_tests:
        test()
    deploy("production")
```

Run the pipeline:

```bash
# Full release
fire deploy.py release

# Skip tests (not recommended)
fire deploy.py release --skip-tests

# Individual steps
fire deploy.py build
fire deploy.py test
fire deploy.py deploy --environment staging
```

---

## Integration

Machineconfig integrates with:

- **Containers**: Docker, Podman (`devops` commands)
- **Cloud Storage**: rclone for sync operations
- **Version Control**: Git operations in scripts
- **Task Runners**: Fire-based execution system
- **Terminal Multiplexers**: Zellij sessions for parallel tasks
