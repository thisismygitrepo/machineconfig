# Configuration Management

Manage system-level configuration across platforms.

---

## Overview

Machineconfig handles configuration for:

- Shell profiles (bash, zsh, fish, nushell, PowerShell)
- Editor settings (VSCode, Vim, Helix, etc.)
- Terminal emulators (Alacritty, WezTerm, Windows Terminal)
- Various CLI tools

---

## Shell Configuration

### Setup Shell Profile

```bash
mcfg shell
```

This configures your shell with:

- Useful aliases
- Environment variables
- Path configuration
- Tool integrations

### Supported Shells

| Shell | Configuration File |
|-------|-------------------|
| Bash | `~/.bashrc` |
| Zsh | `~/.zshrc` |
| Fish | `~/.config/fish/config.fish` |
| Nushell | `~/.config/nushell/config.nu` |
| PowerShell | `$PROFILE` |

---

## Editor Configuration

Machineconfig includes optimized configurations for popular editors:

### Helix

```bash
mcfg config helix
```

### VSCode

```bash
mcfg config vscode
```

### LunarVim

```bash
mcfg config lvim
```

---

## Terminal Configuration

### Alacritty

```bash
mcfg config alacritty
```

### WezTerm

```bash
mcfg config wezterm
```

### Windows Terminal

```bash
mcfg config wt
```

---

## Configuration Files Location

Machineconfig stores its configuration templates in:

```
machineconfig/settings/
├── shells/
│   ├── alacritty/
│   ├── bash/
│   ├── fish/
│   └── ...
├── helix/
├── lvim/
├── yazi/
└── ...
```

---

## Custom Configuration

You can extend or override default configurations:

1. Fork the settings you want to modify
2. Place them in your dotfiles repository
3. Use machineconfig to symlink them

See [Dotfiles](dotfiles.md) for more details.
