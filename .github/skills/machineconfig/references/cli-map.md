# Machineconfig CLI Map

Verified against source and live `--help` output on 2026-03-03.

This reference intentionally uses:
- direct commands only
- canonical command names only

This reference intentionally excludes:
- command aliases

## Direct Entry Points

Defined in `pyproject.toml` `[project.scripts]`:

- `devops` -> `machineconfig.scripts.python.devops:main`
- `cloud` -> `machineconfig.scripts.python.cloud:main`
- `sessions` -> `machineconfig.scripts.python.sessions:main`
- `agents` -> `machineconfig.scripts.python.agents:main`
- `utils` -> `machineconfig.scripts.python.utils:main`
- `fire` -> `machineconfig.scripts.python.fire_jobs:main`
- `croshell` -> `machineconfig.scripts.python.croshell:main`
- `msearch` -> `machineconfig.scripts.python.msearch:main`

## Command Trees

```text
devops
├─ install
├─ repos
│  ├─ sync
│  ├─ register
│  ├─ action
│  ├─ analyze
│  ├─ guard
│  ├─ viz
│  ├─ count-lines
│  ├─ config-linters
│  ├─ cleanup
│  ├─ checkout-to-commit (hidden/deprecated)
│  └─ checkout-to-branch (hidden/deprecated)
├─ config
│  ├─ sync
│  ├─ register
│  ├─ edit
│  ├─ export-dotfiles
│  ├─ import-dotfiles
│  ├─ shell
│  ├─ starship-theme
│  ├─ pwsh-theme
│  ├─ wezterm-theme
│  ├─ ghostty-theme
│  ├─ windows-terminal-theme
│  ├─ copy-assets
│  ├─ dump
│  ├─ list-devices
│  └─ mount
├─ data
│  ├─ sync
│  ├─ register
│  └─ edit
├─ self
│  ├─ update
│  ├─ init
│  ├─ status
│  ├─ install
│  ├─ explore
│  │  ├─ search
│  │  ├─ tree
│  │  ├─ dot
│  │  ├─ sunburst
│  │  ├─ treemap
│  │  ├─ icicle
│  │  └─ tui
│  ├─ readme
│  ├─ buid-docker (conditional)
│  └─ security (conditional)
│     ├─ scan-all
│     ├─ scan
│     ├─ list-all
│     ├─ list
│     ├─ upload
│     ├─ download
│     ├─ install
│     ├─ summary
│     ├─ report
│     └─ scan-path
├─ network
│  ├─ share-terminal
│  ├─ share-server
│  ├─ send
│  ├─ receive
│  ├─ share-temp-file
│  ├─ show-address
│  ├─ switch-public-ip
│  ├─ wifi-select
│  ├─ bind-wsl-port
│  ├─ open-wsl-port
│  ├─ link-wsl-windows
│  ├─ reset-cloudflare-tunnel
│  ├─ add-ip-exclusion-to-warp
│  ├─ vscode-share
│  └─ ssh
│     ├─ install-server
│     ├─ change-port
│     ├─ add-key
│     └─ debug
└─ execute

cloud
├─ sync
├─ copy
├─ mount
└─ ftpx

sessions
├─ run
├─ attach
├─ create-from-function
├─ balance-load
├─ create-template
└─ summarize

agents
├─ create
├─ create-context
├─ collect
├─ make-template
├─ make-config
├─ make-todo
├─ make-symlinks
└─ run-prompt

utils
├─ kill-process
├─ environment
├─ upgrade-packages
├─ download
├─ get-machine-specs
├─ init-project
├─ edit
├─ pdf-merge
├─ pdf-compress
├─ type-hint
└─ read-db

fire
croshell
msearch
```

## Important Nuances

- `devops self security` and `devops self buid-docker` are conditionally registered when `~/code/machineconfig` exists.
- The docs may lag source. Prefer command paths and behavior verified from current Typer source and `--help` output.
