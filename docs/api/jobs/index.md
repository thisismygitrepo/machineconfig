# Jobs Module

The `jobs` module provides functionality for package installation and job execution.

---

## Overview

```python
from machineconfig import jobs
```

---

## Submodules

### Installer

Handles package installation across platforms:

- Package detection
- Installation verification
- Package groups

[:octicons-arrow-right-24: Installer Documentation](installer.md)

---

## Package Groups

Machineconfig defines package groups for common use cases:

```python
from machineconfig.jobs.installer import package_groups

# Get all packages in a group
dev_packages = package_groups.get_group("dev")
```
