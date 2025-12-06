# Quickstart

Get up and running with Machineconfig in minutes.

---

## Interactive Setup (Recommended)

The easiest way to get started is with our interactive installer:

=== "Linux / macOS"

    ```bash
    . <(curl -L bit.ly/cfglinux)
    ```

=== "Windows"

    ```powershell
    irm bit.ly/cfgwindows | iex
    ```

This will guide you through:

1. Installing machineconfig
2. Selecting your preferred tools
3. Configuring your environment
4. Setting up dotfiles

---

## Quick Setup (Accept Defaults)

For a quick setup that accepts all recommended defaults:

=== "Windows"

    ```powershell
    irm bit.ly/cfgwq | iex
    ```

---

## Manual First Steps

After installing machineconfig, here are the essential commands to know:

### 1. Check Available Commands

```bash
mcfg --help
```

### 2. Configure Your Shell

```bash
mcfg shell
```

This sets up your shell profile with useful aliases and functions.

### 3. Install Essential Tools

```bash
devops install-essentials
```

Installs a curated set of modern CLI tools.

### 4. Sync Your Dotfiles

```bash
mcfg dotfiles sync
```

---

## Available CLI Tools

After installation, you have access to these commands:

| Command | Description |
|---------|-------------|
| `mcfg` | Main entry point for machineconfig |
| `devops` | DevOps and system administration tasks |
| `cloud` | Cloud provider management |
| `sessions` | Terminal session management |
| `fire` | Fire-based job execution |
| `agents` | AI agent utilities |
| `croshell` | Cross-shell utilities |
| `ftpx` | FTP/SFTP utilities |
| `terminal` | Terminal configuration |
| `msearch` | Search utilities |

---

## Next Steps

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **Read the User Guide**

    ---

    Learn about all features in depth

    [:octicons-arrow-right-24: User Guide](guide/overview.md)

-   :material-console:{ .lg .middle } **Explore CLI Commands**

    ---

    Full reference for all commands

    [:octicons-arrow-right-24: CLI Reference](cli/index.md)

</div>
