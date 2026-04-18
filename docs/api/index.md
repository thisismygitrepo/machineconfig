# API Reference

`machineconfig` is easiest to approach as three connected layers:

- `machineconfig.utils` for shared helpers and script-generation glue
- `machineconfig.cluster` for layouts, terminal sessions, and remote execution
- `machineconfig.jobs.installer` plus `machineconfig.utils.installer_utils` for curated installers

This reference follows those workflows instead of mirroring the raw package tree.

---

## Integration areas

| Area | What it covers | Main modules | Reference |
| --- | --- | --- | --- |
| Environment and project wiring | `.ve.yaml` discovery, optional IPython profile lookup, cloud metadata defaults | `machineconfig.utils.ve` | [Environment and project wiring](utils/environment-and-projects.md) |
| Paths, files, and config documents | JSON / INI / pickle IO, GPG helpers, path mutation, path-reference lookup | `machineconfig.utils.io`, `machineconfig.utils.path_core`, `machineconfig.utils.path_helper`, `machineconfig.utils.path_reference` | [Paths, files, and config](utils/paths-files-config.md) |
| Scheduling and cache | Repeating routines, memory cache, disk-backed cache | `machineconfig.utils.scheduler` | [Scheduling and cache](utils/scheduling-and-cache.md) |
| Interactive helpers and notifications | IDs, list splitting, fuzzy / TV-backed choices, HTML email | `machineconfig.utils.accessories`, `machineconfig.utils.options`, `machineconfig.utils.notifications` | [Interactive helpers and notifications](utils/interactive-helpers.md) |
| Code generation and command launching | Lambda-to-script conversion, `uv` command builders, shell execution, shell handoff | `machineconfig.utils.meta`, `machineconfig.utils.code`, `machineconfig.utils.installer_utils.installer_cli` | [Code generation and command launching](utils/code-generation.md) |
| Session layouts and orchestration | Layout schema, tab builders, tab splitting, zellij / tmux / Windows Terminal backends | `machineconfig.utils.schemas.layouts.layout_types`, `machineconfig.cluster.sessions_managers.*` | [Layouts](cluster/layouts.md), [Sessions](cluster/sessions.md) |
| Remote execution and networking | Remote job config and state, transfer, SSH, public-IP and LAN helpers | `machineconfig.cluster.remote.*`, `machineconfig.utils.ssh`, `machineconfig.scripts.python.helpers.helpers_network.*` | [Remote execution and networking](cluster/remote.md) |
| Installer catalog and package groups | Installer data, package groups, install orchestration, direct URL installers | `machineconfig.jobs.installer.*`, `machineconfig.utils.installer_utils.*`, `machineconfig.utils.schemas.installer.installer_types` | [Jobs and installer APIs](jobs/index.md) |

---

## Package map

```text
machineconfig/
├── cluster/
│   ├── remote/                    # Remote job models, transfer, script generation
│   └── sessions_managers/         # zellij, tmux, Windows Terminal backends
├── jobs/
│   └── installer/                 # installer_data.json, package groups, install scripts
├── scripts/python/helpers/
│   └── helpers_network/           # IP and connectivity helpers
├── utils/
│   ├── accessories, code, io, meta, notifications, options, scheduler, ssh, ve
│   ├── installer_utils/           # Runtime installer engine
│   ├── path_core, path_helper, path_reference
│   └── schemas/{installer,layouts}
└── settings/                      # Configuration assets and templates
```

---

## Choose a reference track

### Utilities

Start here if you are importing helper APIs into your own scripts or applications:

- [Utils overview](utils/index.md)
- [Environment and project wiring](utils/environment-and-projects.md)
- [Paths, files, and config](utils/paths-files-config.md)
- [Scheduling and cache](utils/scheduling-and-cache.md)
- [Interactive helpers and notifications](utils/interactive-helpers.md)
- [Code generation and command launching](utils/code-generation.md)

### Cluster and remote execution

Start here if you are generating layouts, managing terminal sessions, or submitting jobs to other machines:

- [Cluster overview](cluster/index.md)
- [Layouts](cluster/layouts.md)
- [Sessions](cluster/sessions.md)
- [Remote execution and networking](cluster/remote.md)

### Jobs and installers

Start here if you need the curated installer catalog, group definitions, or install orchestration helpers:

- [Jobs overview](jobs/index.md)
- [Installer reference](jobs/installer.md)

---

## Common import patterns

```python
from machineconfig.cluster.remote.models import RemoteMachineConfig
from machineconfig.cluster.remote.remote_machine import RemoteMachine
from machineconfig.cluster.sessions_managers.utils.maker import make_layout_from_functions
from machineconfig.jobs.installer.package_groups import PACKAGE_GROUP2NAMES
from machineconfig.utils.code import run_shell_script
from machineconfig.utils.installer_utils.installer_cli import install_if_missing
from machineconfig.utils.scheduler import Scheduler, Cache
```

If you need end-user command entrypoints instead of library APIs, see the [CLI Reference](../cli/index.md).
