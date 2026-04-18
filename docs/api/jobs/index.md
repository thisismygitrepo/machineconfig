# Jobs and Installer APIs

`machineconfig.jobs` is mostly the data and asset layer for the installer system. It ships:

- the installer catalog JSON
- package-group definitions
- platform-specific install scripts
- security-check helpers

The runtime installation engine that consumes those assets lives under `machineconfig.utils.installer_utils`.

---

## What lives here

| Area | What it provides | Main modules |
| --- | --- | --- |
| Package groups | Named collections of apps such as `termabc`, `agents`, `dev`, and `db-cli` | `machineconfig.jobs.installer.package_groups` |
| Installer catalog assets | `installer_data.json` path references and packaged installer scripts | `machineconfig.jobs.installer`, `machineconfig.jobs.installer.python_scripts.*`, `machineconfig.jobs.installer.linux_scripts.*`, `machineconfig.jobs.installer.powershell_scripts.*` |
| Installer runtime | CLI entrypoints, installer selection, bulk install orchestration, direct URL install | `machineconfig.utils.installer_utils.*` |
| Typed installer schema | Platform names, architecture names, install requests, install results | `machineconfig.utils.schemas.installer.installer_types` |
| Security checks | Scan and reporting helpers for installed tools | `machineconfig.jobs.installer.checks.*` |

---

## Package groups

The current `PACKAGE_GROUP2NAMES` keys are:

- `sysabc`
- `shell`
- `search`
- `sys-monitor`
- `code-analysis`
- `termabc`
- `dev`
- `dev-utils`
- `eye`
- `agents`
- `terminal`
- `browsers`
- `editors`
- `db-all`
- `db-cli`
- `db-desktop`
- `db-web`
- `db-tui`
- `media`
- `gui`
- `nw`
- `file-sharing`
- `productivity`

Example:

```python
from machineconfig.jobs.installer.package_groups import PACKAGE_GROUP2NAMES

print(PACKAGE_GROUP2NAMES["agents"])
print(PACKAGE_GROUP2NAMES["termabc"])
```

---

## Relationship to the installer helpers

The runtime path looks like this:

1. `jobs/installer/installer_data.json` defines the catalog.
2. `jobs/installer/package_groups.py` defines named bundles.
3. `machineconfig.utils.installer_utils.installer_runner.get_installers()` filters that catalog for the current OS, architecture, and optional groups.
4. `machineconfig.utils.installer_utils.installer_class.Installer` resolves and executes one install target.
5. `machineconfig.utils.installer_utils.installer_cli` exposes the higher-level CLI-style entrypoints.

So this section documents both the packaged job assets and the installer APIs that consume them.

---

## Directory layout

```text
jobs/installer/
├── installer_data.json     # Catalog of installer definitions
├── package_groups.py       # Named package bundles
├── checks/                 # Security and reporting helpers
├── linux_scripts/          # Linux and macOS shell installers
├── powershell_scripts/     # Windows PowerShell installers
└── python_scripts/         # Custom Python installers
```

---

## Next page

Continue to the [Installer reference](installer.md) for the current data model, install strategies, group handling, and callable entrypoints.
