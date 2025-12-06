# Jobs Module

The `jobs` module provides functionality for package installation, job execution, and system setup.

---

## Overview

```python
from machineconfig import jobs
```

The jobs module contains:

- **Installer** - Cross-platform package installation system
- **Scripts** - Installation scripts for various platforms

---

## Submodules

### Installer

Handles package installation across platforms:

- Package detection and verification
- Cross-platform installation commands
- Package groups for batch installation
- VirusTotal integration for security scanning

[:octicons-arrow-right-24: Installer Documentation](installer.md)

---

## Package Groups

Machineconfig defines curated package groups for common use cases:

| Group | Description | Package Count |
|-------|-------------|---------------|
| `gui` | Essential GUI applications (Brave, VS Code, Git) | 3 |
| `agents` | AI/LLM coding assistants (aider, copilot, etc.) | 14+ |
| `termabc` | Terminal essentials (analysis, monitors, shell tools) | 40+ |
| `dev` | Full development environment | 80+ |
| `sysabc` | System ABC utilities | 1 |

### Using Package Groups

```bash
# Install all packages in a group
devops install-group dev

# Install specific group
devops install-group agents
```

### Available Groups

```python
from machineconfig.jobs.installer.package_groups import PACKAGE_GROUP2NAMES

# List all groups
print(PACKAGE_GROUP2NAMES.keys())
# dict_keys(['sysabc', 'termabc', 'gui', 'dev', 'dev-utils', ...])

# Get packages in a group
print(PACKAGE_GROUP2NAMES['agents'])
# ['aider', 'aichat', 'copilot', 'gemini', ...]
```

---

## Package Categories

### AI/LLM Tools (`agents`)

AI-powered coding and chat assistants:

- `aider` - AI pair programming
- `copilot` - GitHub Copilot CLI
- `opencode-ai` - OpenCode AI assistant
- `chatgpt` - ChatGPT CLI
- `mods` - AI in the terminal
- And more...

### Terminal Essentials (`termabc`)

Must-have terminal tools:

- **File Search**: `fd`, `fzf`, `rg`, `broot`
- **File Management**: `yazi`, `tere`, `lsd`, `zoxide`
- **System Monitors**: `btop`, `btm`, `procs`, `bandwhich`
- **Shell Tools**: `zellij`, `starship`, `atuin`, `mcfly`

### Development Tools (`dev`)

Full development setup:

- **Editors**: VS Code, Cursor, LunarVim
- **Browsers**: Brave, terminal browsers
- **Databases**: SQLite, DuckDB, Redis, DBeaver
- **Productivity**: espanso, glow, pandoc

---

## Installation Data

Package installation data is stored in `installer_data.json`:

```json
{
  "packages": [
    {
      "appName": "btop",
      "description": "Resource monitor",
      "platforms": {
        "linux": {"apt": "btop", "cargo": "btop"},
        "darwin": {"brew": "btop"},
        "windows": {"scoop": "btop", "winget": "btop"}
      }
    }
  ]
}
```

---

## Scripts

Platform-specific installation scripts:

```
jobs/installer/
├── linux_scripts/     # Bash scripts for Linux
├── powershell_scripts/  # PowerShell for Windows
└── python_scripts/    # Cross-platform Python installers
```

### Python Scripts

Custom installers for complex packages:

```python
# Example: Install Helix editor with language support
from machineconfig.jobs.installer.python_scripts import hx
hx.install()
```
