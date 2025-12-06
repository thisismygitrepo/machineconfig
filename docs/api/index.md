# API Reference

This section provides detailed API documentation for the Machineconfig Python package.

---

## Package Structure

```
machineconfig/
├── cluster/           # Cluster and remote operations
│   ├── remote/        # Remote machine management
│   └── sessions_managers/  # Session management
├── jobs/              # Job execution
│   └── installer/     # Package installation
├── scripts/           # CLI script implementations
├── utils/             # Utility functions
└── settings/          # Configuration templates
```

---

## Core Modules

### Cluster Operations

The `cluster` module handles remote machine operations:

- [Remote](cluster/remote.md) - Remote machine connectivity
- [Sessions](cluster/sessions.md) - Session management

### Jobs

The `jobs` module provides job execution:

- [Installer](jobs/installer.md) - Package installation utilities

### Utilities

The `utils` module contains helper functions:

- [Utils Overview](utils/index.md) - Common utilities

---

## Quick Example

```python
from machineconfig.utils import path_extended

# Use extended path utilities
p = path_extended.PathPlus("~/documents")
print(p.expanduser())
```

---

## Import Patterns

```python
# Import specific modules
from machineconfig.cluster.remote import remote_machine
from machineconfig.jobs.installer import package_groups
from machineconfig.utils import accessories

# Import main package
import machineconfig
```
