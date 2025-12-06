# CLI Reference

Machineconfig provides several command-line tools for different purposes.

---

## Available Commands

| Command | Description |
|---------|-------------|
| [`mcfg`](mcfg.md) | Main entry point - configuration and setup |
| [`devops`](devops.md) | DevOps operations and package management |
| [`cloud`](cloud.md) | Cloud provider and data sync operations |
| [`sessions`](sessions.md) | Terminal session management |
| [`fire`](fire.md) | Fire-based job execution |

---

## Additional Commands

| Command | Description |
|---------|-------------|
| `agents` | AI agent utilities |
| `croshell` | Cross-shell utilities |
| `ftpx` | FTP/SFTP utilities |
| `terminal` | Terminal configuration |
| `msearch` | Search utilities |
| `utils` | General utilities |

---

## Getting Help

Every command supports `--help`:

```bash
mcfg --help
devops --help
cloud sync --help
```

---

## Command Structure

Most commands follow this pattern:

```bash
command [subcommand] [options] [arguments]
```

### Examples

```bash
# Main command with subcommand
devops install ripgrep

# Command with options
cloud sync --dry-run ~/data remote:backup

# Command with flags
sessions list --all
```

---

## Global Options

These options are available for most commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version |
| `--verbose` | Enable verbose output |
| `--quiet` | Suppress output |
| `--dry-run` | Preview without making changes |

---

## Shell Completion

Enable shell completion for better CLI experience:

=== "Bash"

    ```bash
    eval "$(mcfg --install-completion bash)"
    ```

=== "Zsh"

    ```bash
    eval "$(mcfg --install-completion zsh)"
    ```

=== "Fish"

    ```fish
    mcfg --install-completion fish | source
    ```

=== "PowerShell"

    ```powershell
    mcfg --install-completion powershell | Out-String | Invoke-Expression
    ```
