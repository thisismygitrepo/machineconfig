# Utils Module

The `utils` module provides utility functions and helpers used throughout Machineconfig.

---

## Overview

```python
from machineconfig import utils
```

The utils module contains:

- **Path utilities** - Extended path operations
- **SSH utilities** - SSH connection helpers
- **Scheduler** - Task scheduling and execution
- **Installer utilities** - Package installation helpers
- **I/O utilities** - File reading/writing helpers
- **Accessories** - General helper functions

---

## Key Modules

### Scheduler

A flexible task scheduler for running recurring operations:

```python
from machineconfig.utils.scheduler import Scheduler
import logging

logger = logging.getLogger(__name__)

def my_routine(scheduler: Scheduler):
    """Task to run on each cycle."""
    print(f"Running cycle {scheduler.cycle}")

# Create scheduler - runs every 60 seconds
sched = Scheduler(
    routine=my_routine,
    wait_ms=60_000,  # 60 seconds
    logger=logger,
    max_cycles=100,
)

# Run the scheduler
sched.run()
```

---

### Accessories

General helper functions:

```python
from machineconfig.utils.accessories import randstr, split_list, pprint

# Generate random strings
token = randstr(length=16, safe=True)  # Cryptographically secure
name = randstr(noun=True)  # Random noun (e.g., "happy-dolphin")

# Split lists
chunks = split_list([1, 2, 3, 4, 5, 6, 7, 8], every=3)
# [[1, 2, 3], [4, 5, 6], [7, 8]]

parts = split_list([1, 2, 3, 4, 5, 6, 7, 8], to=3)
# [[1, 2, 3], [4, 5, 6], [7, 8]]

# Pretty print dictionaries
pprint({"name": "test", "value": 42}, title="My Data")
```

---

### SSH Utilities

SSH connection and file transfer helpers:

```python
from machineconfig.utils.ssh import SSH

# Create SSH connection
ssh = SSH(host="server.example.com", username="user")

# Execute command
result = ssh.run("ls -la")
print(result.stdout)

# Transfer files
ssh.upload("local_file.txt", "/remote/path/file.txt")
ssh.download("/remote/path/file.txt", "local_file.txt")
```

#### WSL Utilities

For Windows Subsystem for Linux:

```python
from machineconfig.utils.ssh_utils import wsl

# Get WSL home directory
wsl_home = wsl.get_wsl_home()

# Open firewall ports for WSL
wsl.open_wsl_ports([8000, 8080, 3000])
```

---

### Installer Utilities

Helpers for package installation:

```python
from machineconfig.utils.installer_utils import install_from_url

# Install from GitHub release
install_from_url.install_github_release(
    repo="owner/repo",
    asset_pattern="*linux*amd64*",
    install_dir="/usr/local/bin"
)
```

---

### I/O Utilities

File reading and writing:

```python
from machineconfig.utils.io import from_pickle, to_pickle

# Pickle operations
data = {"key": "value"}
to_pickle(data, "data.pkl")
loaded = from_pickle("data.pkl")
```

---

### Terminal Utilities

Terminal interaction helpers:

```python
from machineconfig.utils.terminal import run_command

# Run shell command
result = run_command("echo hello")
print(result.stdout)
```

---

### Options

Interactive option selection:

```python
from machineconfig.utils.options import choose_from_options

# Interactive selection
choice = choose_from_options(
    options=["option1", "option2", "option3"],
    msg="Select an option:",
    multi=False,
)
```

With Television (TV) fuzzy finder:

```python
from machineconfig.utils.options_tv import choose_from_options_tv

# Fuzzy selection with TV
choice = choose_from_options_tv(
    options=["file1.py", "file2.py", "file3.py"],
    prompt="Select file:",
)
```

---

## Submodules

### AI Utilities

AI and LLM integration helpers.

### Cloud Utilities

Cloud storage integration (OneDrive, etc.).

### File Utilities

- `ascii_art.py` - ASCII art generation
- `dbms.py` - Database management utilities
- `headers.py` - File header parsing
- `read.py` - File reading utilities

### Schema Definitions

Type definitions and JSON schemas:

- `layouts/` - Session layout schemas
- `installer/` - Installer data schemas
- `repos/` - Repository configuration schemas

---

## Path Extended

Extended path operations (deprecated - prefer standard `pathlib.Path`):

::: machineconfig.utils.path_extended
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      show_docstring_description: true

---

## Accessories Reference

::: machineconfig.utils.accessories
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      show_docstring_description: true
