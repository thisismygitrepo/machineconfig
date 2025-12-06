# Sessions Managers

The `sessions_managers` subpackage provides terminal session management functionality.

---

## Overview

Manages terminal sessions using various backends:

- **Windows Terminal (wt)** - Native Windows terminal multiplexing
- **Zellij** - Modern terminal workspace (Linux/macOS)

---

## Session Managers

| Module | Platform | Description |
|--------|----------|-------------|
| `wt_local_manager` | Windows | Local Windows Terminal sessions |
| `wt_remote_manager` | Windows | Remote Windows Terminal sessions |
| `zellij_local_manager` | Linux/macOS | Local Zellij sessions |
| `zellij_remote_manager` | Linux/macOS | Remote Zellij sessions |

---

## Usage Example

```python
from machineconfig.cluster import sessions_managers

# Session management functionality
# ...
```

!!! note "Platform Support"
    Windows Terminal managers work on Windows only.
    Zellij managers work on Linux and macOS.
