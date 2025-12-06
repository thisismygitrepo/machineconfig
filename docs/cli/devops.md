# devops

DevOps operations, package management, and system administration.

---

## Usage

```bash
devops [OPTIONS] COMMAND [ARGS]...
```

---

## Commands Overview

| Command | Shortcut | Description |
|---------|----------|-------------|
| `install` | `i` | Install packages |
| `repos` | `r` | Manage development repositories |
| `config` | `c` | Configuration management |
| `data` | `d` | Data management |
| `self` | `s` | Self management |
| `network` | `n` | Network management |
| `execute` | `e` | Execute scripts |

---

## install

Install packages from various package managers.

```bash
devops install [OPTIONS] [PACKAGES]
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--group` | `-g` | Treat argument as a group name (bundle of apps) |
| `--interactive` | `-i` | Interactive selection of programs to install |

**Examples:**

```bash
# Install specific packages (comma-separated)
devops install btop,fd,bat

# Install a package group
devops install termabc --group

# Interactive package selection
devops install --interactive
```

**Available Package Groups:**

| Group | Description |
|-------|-------------|
| `sysabc` | System ABC utilities |
| `termabc` | Terminal essentials (40+ tools) |
| `gui` | GUI applications |
| `dev` | Full development environment (80+ tools) |
| `agents` | AI/LLM coding assistants |
| `shell` | Shell enhancements |
| `db` | Database tools |
| `sys-monitor` | System monitors |
| `search` | File search tools |

---

## repos

Manage development repositories.

```bash
devops repos [SUBCOMMAND] [ARGS]...
```

Handles cloning, updating, and managing development repositories.

---

## config

Configuration management.

```bash
devops config [SUBCOMMAND] [ARGS]...
```

Manage application configurations, dotfiles, and settings.

---

## data

Data management operations.

```bash
devops data [SUBCOMMAND] [ARGS]...
```

Handle data backup, sync, and management tasks.

---

## self

Self management commands.

```bash
devops self [SUBCOMMAND] [ARGS]...
```

Manage machineconfig itself - updates, configuration, etc.

---

## network

Network management.

```bash
devops network [SUBCOMMAND] [ARGS]...
```

Network configuration and diagnostics.

---

## execute

Execute Python or shell scripts from pre-defined directories.

```bash
devops execute [OPTIONS] [NAME]
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--where` | `-w` | Where to look for scripts: `all`, `private`, `public`, `library`, `dynamic`, `custom` |
| `--interactive` | `-i` | Interactive selection of scripts |
| `--command` | `-c` | Run as command |
| `--list` | `-l` | List available scripts |

**Examples:**

```bash
# Run a script by name
devops execute my_script

# List all available scripts
devops execute --list

# Interactive script selection
devops execute --interactive

# Run from specific location
devops execute my_script --where private
```

---

## Examples

```bash
# Install terminal essentials
devops install termabc -g

# Install AI coding assistants
devops install agents -g

# Interactive package installation
devops install -i

# List available scripts
devops e -l

# Run a custom script
devops e my_automation

# Manage repositories
devops repos clone myrepo

# Network diagnostics
devops network check
```
