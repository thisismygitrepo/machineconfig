# Sessions

The session-manager layer takes `LayoutConfig` objects and turns them into running terminal sessions. The shared pieces are:

- session-name conflict planning
- backend-specific layout launchers
- attach, status, monitoring, and persistence helpers

---

## Supported managers

| Manager | Module path | What it manages |
| --- | --- | --- |
| `ZellijLocalManager` | `machineconfig.cluster.sessions_managers.zellij.zellij_local_manager` | Local zellij sessions generated from `list[LayoutConfig]` |
| `TmuxLocalManager` | `machineconfig.cluster.sessions_managers.tmux.tmux_local_manager` | Local tmux sessions generated from `list[LayoutConfig]` |
| `WTLocalManager` | `machineconfig.cluster.sessions_managers.windows_terminal.wt_local_manager` | Local Windows Terminal sessions generated from `list[LayoutConfig]` |
| `ZellijSessionManager` | `machineconfig.cluster.sessions_managers.zellij.zellij_remote_manager` | Remote zellij sessions across SSH hosts |
| `WTSessionManager` | `machineconfig.cluster.sessions_managers.windows_terminal.wt_remote_manager` | Remote Windows Terminal sessions across remote machines |

---

## Conflict policies

`machineconfig.cluster.sessions_managers.session_conflict` defines the shared conflict planner.

### Supported actions

| Action | Meaning |
| --- | --- |
| `error` | Fail if a requested session already exists or if two requested layouts target the same name |
| `restart` | Reuse the requested name and restart an existing session when necessary |
| `rename` | Keep the requested name as a base and allocate `name_1`, `name_2`, and so on |
| `mergeNewWindowsOverwriteMatchingWindows` | Keep the requested session name and merge new windows into an existing tmux or Windows Terminal session, overwriting matching windows where supported |
| `mergeNewWindowsSkipMatchingWindows` | Keep the requested session name and merge only missing windows where supported |

The two merge actions are only valid for the `tmux` and `windows-terminal` backends.

---

## Backend-specific behavior

### Zellij local

`ZellijLocalManager`:

- always prefixes managed session names with `LocalJobMgr_`
- requires `start_all_sessions(on_conflict, poll_seconds, poll_interval)`
- launches zellij sessions non-blockingly and then polls `zellij list-sessions`
- supports `attach_to_session()`, `check_all_sessions_status()`, `run_monitoring_routine()`, `save()`, `load()`, and `list_active_sessions()`

Example:

```python
from machineconfig.cluster.sessions_managers.zellij.zellij_local_manager import ZellijLocalManager

manager = ZellijLocalManager(session_layouts=[layout])
manager.start_all_sessions(
    on_conflict="rename",
    poll_seconds=10.0,
    poll_interval=0.5,
)
print(manager.attach_to_session(None))
```

### tmux local

`TmuxLocalManager` requires explicit `session_name_prefix` and `exit_mode` values:

```python
from machineconfig.cluster.sessions_managers.tmux.tmux_local_manager import TmuxLocalManager

manager = TmuxLocalManager(
    session_layouts=[layout],
    session_name_prefix="ops",
    exit_mode="backToShell",
)

manager.start_all_sessions(on_conflict="rename")
print(manager.attach_to_session(None))
report = manager.check_all_sessions_status()
```

tmux is also the backend where merge conflict actions produce merge scripts instead of only rename-or-restart plans.

### Windows Terminal local

`WTLocalManager` also takes `session_layouts`, `session_name_prefix`, and `exit_mode`, but `start_all_sessions()` currently has no `on_conflict` parameter. It simply runs the generated PowerShell launcher for each managed layout.

Useful current helpers include:

- `attach_to_session()`
- `check_all_sessions_status()`
- `run_monitoring_routine()`
- `save()` / `load()`
- `get_wt_overview()`
- `list_active_sessions()`

### Remote managers

The remote managers keep the same status and persistence ideas, but their inputs are backend-specific:

- `ZellijSessionManager(machine_layouts: dict[str, LayoutConfig], session_name_prefix: str)`
- `WTSessionManager(machine2wt_tabs: dict[str, dict[str, tuple[str, str]]], session_name_prefix: str | None = "WTJobMgr")`

Representative helpers:

- `ssh_to_all_machines()`
- `start_all_sessions()` or `start_zellij_sessions()`
- `run_monitoring_routine()`
- `save()` / `load()`

---

## Monitoring and reporting helpers

Representative utility modules include:

- `machineconfig.cluster.sessions_managers.zellij.zellij_utils.process_monitor`
- `machineconfig.cluster.sessions_managers.zellij.zellij_utils.status_reporter`
- `machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.status_reporting`
- `machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.manager_persistence`

These modules power the status summaries returned by the manager classes rather than replacing them.

---

## See also

- [Layouts](layouts.md) for `LayoutConfig`, layout serialization, and tab generation
- [Remote execution and networking](remote.md) for remote-job flows that feed these backends
- [CLI Terminal Reference](../../cli/terminal.md) for the end-user command layer

---

## API reference

## Conflict planning

::: machineconfig.cluster.sessions_managers.session_conflict
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Zellij local manager

::: machineconfig.cluster.sessions_managers.zellij.zellij_local_manager
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## tmux local manager

::: machineconfig.cluster.sessions_managers.tmux.tmux_local_manager
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Windows Terminal local manager

::: machineconfig.cluster.sessions_managers.windows_terminal.wt_local_manager
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Zellij remote manager

::: machineconfig.cluster.sessions_managers.zellij.zellij_remote_manager
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Windows Terminal remote manager

::: machineconfig.cluster.sessions_managers.windows_terminal.wt_remote_manager
    options:
      show_root_heading: true
      show_source: false
      members_order: source
