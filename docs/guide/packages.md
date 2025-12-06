# Package Management

Machineconfig provides unified package management across all platforms.

---

## Overview

Instead of learning different package managers for each OS, machineconfig provides a consistent interface:

| Platform | Underlying Package Manager |
|----------|---------------------------|
| Linux (Debian/Ubuntu) | `apt` |
| Linux (Arch) | `pacman` |
| Linux (Fedora) | `dnf` |
| macOS | `brew` |
| Windows | `winget`, `scoop` |

---

## Installing Packages

### Single Package

```bash
devops install <package-name>
```

### Multiple Packages

```bash
devops install package1 package2 package3
```

### From a List

```bash
devops install-from-list packages.txt
```

---

## Essential Packages

Machineconfig comes with a curated list of modern CLI tools:

```bash
devops install-essentials
```

This installs tools like:

- **fd** - Modern `find` alternative
- **ripgrep** - Modern `grep` alternative  
- **bat** - Modern `cat` alternative
- **exa/eza** - Modern `ls` alternative
- **fzf** - Fuzzy finder
- **zoxide** - Smarter `cd`
- **starship** - Cross-shell prompt
- And many more...

---

## Package Groups

Install predefined groups of packages:

```bash
# Development essentials
devops install-group dev

# System utilities
devops install-group sysadmin

# Data science tools
devops install-group datascience
```

---

## Checking Installations

Verify what's installed:

```bash
devops check-installations
```

This provides a comprehensive report of installed tools and their versions.

---

## Updating Packages

Keep your tools up to date:

```bash
devops update-all
```
