# devops

`devops` is the main operational CLI for package installation, repo automation, config sync, data sync, self-management, networking, and script execution.

---

## Usage

```bash
devops [OPTIONS] COMMAND [ARGS]...
```

## Current top-level commands

| Command | Purpose |
| --- | --- |
| `install` | Install packages or named groups |
| `repos` | Manage development repositories |
| `config` | Configuration and dotfile workflows |
| `data` | Backup and restore configured data paths |
| `self` | Machineconfig self-management and developer workflows |
| `network` | Sharing, transfer, address, SSH, and device helpers |
| `execute` | Run scripts from predefined locations or as a raw command |

---

## `install`

```bash
devops install [OPTIONS] [WHICH]
```

Current options:

- `--group` to treat `WHICH` as a bundle name
- `--interactive` to choose packages interactively
- `--update` to reinstall or upgrade when supported
- `--version` to request a specific version or tag

Example:

```bash
devops install --group sysabc
devops install lazygit,fd --update
```

---

## Current command groups

These are the child commands exposed by the current live help.

`repos`:

- `sync`
- `register`
- `action`
- `analyze`
- `guard`
- `viz`
- `count-lines`
- `config-linters`
- `cleanup`

`config`:

- `sync`
- `register`
- `edit`
- `export-dotfiles`
- `import-dotfiles`
- `copy-assets`
- `dump`
- `terminal`

`data`:

- `sync`
- `register`
- `edit`

`self`:

- `install`
- `update`
- `status`
- `config`
- `security`
- `init`
- `explore`
- `readme`
- `docs`
- `build-installer`
- `build-docker`
- `build-assets`
- `workflows`

`network`:

- `share-terminal`
- `share-server`
- `send`
- `receive`
- `share-temp-file`
- `show-address`
- `vscode-share`
- `ssh`
- `device`

---

## `execute`

```bash
devops execute [OPTIONS] [NAME]
```

Current behavior:

- `NAME` can be a predefined script name or a raw command string
- `--where` selects search locations: `all`, `private`, `public`, `library`, `dynamic`, or `custom`
- `--interactive` enables interactive selection
- `--command` runs the input as a command
- `--list` prints the available scripts

Examples:

```bash
devops execute --list
devops execute deploy -w library
devops execute "echo hello" --command
```

---

## Working with nested apps

The nested groups above are lazily loaded Typer apps. The exact leaf commands and flags live under those subtrees, so use help at the branch you care about:

```bash
devops repos --help
devops config --help
devops data --help
devops self --help
devops network --help
devops self docs --help
devops config terminal --help
```
