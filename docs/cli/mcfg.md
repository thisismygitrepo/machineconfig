# mcfg

The main entry point for Machineconfig operations.

---

## Usage

```bash
mcfg [OPTIONS] COMMAND [ARGS]...
```

---

## Commands

### shell

Configure shell profile with aliases and integrations.

```bash
mcfg shell [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--shell` | Target shell (bash, zsh, fish, nu, pwsh) |
| `--backup` | Backup existing config first |

---

### config

Apply configuration for various tools.

```bash
mcfg config [TOOL] [OPTIONS]
```

**Supported Tools:**

- `helix` - Helix editor
- `alacritty` - Alacritty terminal
- `wezterm` - WezTerm terminal
- `vscode` - Visual Studio Code
- `lvim` - LunarVim

**Example:**

```bash
mcfg config helix
```

---

### dotfiles

Manage dotfiles synchronization.

```bash
mcfg dotfiles [SUBCOMMAND]
```

**Subcommands:**

| Subcommand | Description |
|------------|-------------|
| `init` | Initialize dotfiles repository |
| `sync` | Sync dotfiles from repository |
| `push` | Push local changes to repository |
| `backup` | Backup current dotfiles |
| `restore` | Restore from backup |

---

### define

Generate installation scripts for new machines.

```bash
mcfg define [OPTIONS]
```

Outputs a script that can bootstrap machineconfig on a new machine.

---

### links

Manage symbolic links for configuration files.

```bash
mcfg links [SUBCOMMAND]
```

**Subcommands:**

| Subcommand | Description |
|------------|-------------|
| `create` | Create symbolic links |
| `remove` | Remove symbolic links |
| `list` | List managed links |

---

## Examples

```bash
# Setup shell with all integrations
mcfg shell

# Apply helix editor configuration
mcfg config helix

# Sync dotfiles from repository
mcfg dotfiles sync

# Create symlinks for configs
mcfg links create
```
