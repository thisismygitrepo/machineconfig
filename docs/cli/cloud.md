# cloud

`cloud` is the direct entrypoint for Machineconfig's cloud copy, sync, mount, and SSH-transfer helpers.

---

## Usage

```bash
cloud [OPTIONS] COMMAND [ARGS]...
```

Current top-level commands:

| Command | Purpose |
| --- | --- |
| `sync` | Synchronize files or folders between local and cloud storage |
| `copy` | Upload or download files and folders |
| `mount` | Mount a configured cloud target locally |
| `ftpx` | Transfer files through SSH using `machine:path` endpoints |

The command also defines hidden one-letter aliases for the same actions: `s`, `c`, `m`, and `f`.

---

## Defaults

When a command does not override them, cloud defaults come from `machineconfig.utils.ve.read_default_cloud_config()`:

- remote root: `myhome`
- `encrypt`, `zip`, `share`, `overwrite`, `os_specific`, `rel2home`: `False`
- `key` and `pwd`: unset

---

## `sync`

```bash
cloud sync [OPTIONS] SOURCE TARGET
```

Current options from live help:

| Option | Meaning |
| --- | --- |
| `--config`, `-c` | Path to `.ve.yaml` |
| `--transfers`, `-t` | Number of sync threads |
| `--root`, `-R` | Remote root |
| `--key`, `-k` | Encryption key |
| `--pwd`, `-P` | Encryption password |
| `--encrypt`, `-e` | Current help text: decrypt after receiving |
| `--zip`, `-z` | Current help text: unzip after receiving |
| `--bisync`, `-b` | Bidirectional sync |
| `--delete`, `-D` | Delete remote files not present locally |
| `--verbose`, `-v` | Show more sync details |

Example:

```bash
cloud sync ~/documents remote:documents --bisync
```

---

## `copy`

```bash
cloud copy [OPTIONS] SOURCE TARGET
```

Current options from live help:

| Option | Meaning |
| --- | --- |
| `--overwrite`, `-o` | Overwrite an existing destination file |
| `--share`, `-s` | Share a file or directory |
| `--relative2home`, `-r` | Treat remote paths as relative to `myhome` |
| `--root`, `-R` | Remote root |
| `--key`, `-k` | Encryption key |
| `--password`, `-p` | Encryption password |
| `--encrypt`, `-e` | Encrypt before sending |
| `--zip`, `-z` | Current help text: unzip after receiving |
| `--os-specific`, `-O` | Choose a path specific to the current OS |
| `--config`, `-c` | Path to `.ve.yaml` |

Example:

```bash
cloud copy ./report.pdf remote:reports/report.pdf
```

---

## `mount`

```bash
cloud mount [OPTIONS]
```

Current options:

| Option | Meaning |
| --- | --- |
| `--cloud`, `-c` | Cloud name to mount |
| `--destination`, `-d` | Mount destination |
| `--network`, `-n` | Network mount target |
| `--backend`, `-b` | Linux/macOS terminal backend: `zellij`, `tmux`, or `auto` |
| `--interactive`, `-i` | Choose the cloud interactively from config |

Current defaults:

- backend: `tmux`
- interactive selection: enabled

---

## `ftpx`

```bash
cloud ftpx [OPTIONS] SOURCE TARGET
```

`SOURCE` and `TARGET` use `machine:path` notation.

Current options:

| Option | Meaning |
| --- | --- |
| `--recursive`, `-r` | Transfer recursively |
| `--zipFirst`, `-z` | Zip before sending |
| `--cloud`, `-c` | Transfer through the cloud |
| `--overwrite-existing`, `-o` | Overwrite existing remote files when sending local to remote |

Example:

```bash
cloud ftpx localmachine:/tmp/archive remotehost:/tmp/archive --recursive
```

---

## Getting help

```bash
cloud --help
cloud sync --help
cloud copy --help
cloud mount --help
cloud ftpx --help
```
