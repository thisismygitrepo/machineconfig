# Layouts

The layout APIs turn Python intent into terminal structure. They define tabs, serialize layouts, build tab commands from callables, and split oversized layouts before handing them to zellij, tmux, or Windows Terminal backends.

---

## Layout schema

The schema lives in `machineconfig.utils.schemas.layouts.layout_types`.

### Core types

| Type | Fields |
| --- | --- |
| `TabConfig` | `tabName`, `startDir`, `command`, optional `tabWeight` |
| `LayoutConfig` | `layoutName`, `layoutTabs` |
| `LayoutsFile` | `version`, `layouts` |

### Helper behavior

- `serialize_layouts_to_file(layouts, version, path)` writes a new layout file with `"$schema": "https://bit.ly/cfglayout"`.
- If the target file already exists, `serialize_layouts_to_file()` replaces layouts that share the same `layoutName` and appends new ones.
- `substitute_home(tabs)` expands `~` and `$HOME` and rewrites shorthand command prefixes:
  - `f ...` -> `~/.config/machineconfig/scripts/wrap_mcfg fire ...`
  - `t ...` -> `~/.config/machineconfig/scripts/wrap_mcfg terminal ...`
  - `s ...` -> `~/.config/machineconfig/scripts/wrap_mcfg seek ...`

The current schema key is `layoutTabs`. There is no alternate `tabs` field in the typed definitions.

---

## Building layouts from Python functions

`machineconfig.cluster.sessions_managers.utils.maker` converts Python callables into `TabConfig` entries.

### Main helpers

| Helper | Purpose |
| --- | --- |
| `get_fire_tab_using_uv()` | Generates Python source from a callable, writes a temporary script, and returns the tab config plus the generated file path |
| `get_fire_tab_using_fire()` | Builds a `wrap_mcfg fire ...` command for an importable callable |
| `make_layout_from_functions()` | Builds a `LayoutConfig` from functions plus any extra tabs you want to append |

`make_layout_from_functions()` accepts both launch styles through `method`:

- `"script"` to execute generated Python through `uv`
- `"fire"` to use the `wrap_mcfg fire` entrypoint

Its `flags` parameter is passed through to the selected launch mode as either `uv_run_flags` or `fire_flags`.

### Example

```python
from machineconfig.cluster.sessions_managers.tmux.tmux_local import run_tmux_layout
from machineconfig.cluster.sessions_managers.utils.maker import make_layout_from_functions


def ingest() -> None:
    print("ingest")


def train() -> None:
    print("train")


layout = make_layout_from_functions(
    functions=[ingest, train],
    functions_weights=[1, 2],
    import_module=True,
    tab_configs=[],
    layout_name="ml-workflow",
    method="script",
    uv_with=["machineconfig"],
    uv_project_dir=None,
    flags="",
    start_dir="~/code/my-project",
)

run_tmux_layout(layout_config=layout, on_conflict="rename")
```

If `functions_weights` is `None`, each function is treated as weight `1`.

---

## Controlling layout size

`machineconfig.cluster.sessions_managers.utils.load_balancer` provides two controls.

### `limit_tab_num()`

```python
limit_tab_num(
    layout_configs=layouts,
    max_thresh=8,
    threshold_type="number",
    breaking_method="moreLayouts",
)
```

Supported `threshold_type` values:

- `"number"` for raw tab count
- `"weight"` for summed `tabWeight`

Supported `breaking_method` values:

- `"moreLayouts"`
- `"combineTabs"`

### `limit_tab_weight()`

`limit_tab_weight(layout_configs, max_weight, command_splitter)` rewrites overweight tabs by calling your `command_splitter(command, to=max_weight)` function and replacing the original tab with `..._part1`, `..._part2`, and so on.

### Convenience launcher

`load_balancer.run(layouts, on_conflict)` is a thin helper that:

1. creates a `ZellijLocalManager`
2. starts all sessions
3. runs the monitoring routine
4. kills all managed sessions when monitoring finishes

---

## Backend-specific layout generators

The same `LayoutConfig` can be handed to multiple backends:

- `run_zellij_layout(layout_config, on_conflict)`
- `run_tmux_layout(layout_config, on_conflict)`
- `run_wt_layout(layout_config, exit_mode)`

Their generator classes are:

- `ZellijLayoutGenerator`
- `TmuxLayoutGenerator`
- `WTLayoutGenerator`

Those classes are responsible for rendering backend-specific layout artifacts:

- zellij KDL files
- tmux shell scripts
- Windows Terminal PowerShell scripts

---

## API reference

## Layout schema

::: machineconfig.utils.schemas.layouts.layout_types
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Layout builders

::: machineconfig.cluster.sessions_managers.utils.maker
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Layout load balancer

::: machineconfig.cluster.sessions_managers.utils.load_balancer
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Zellij layout helpers

::: machineconfig.cluster.sessions_managers.zellij.zellij_local
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## tmux layout helpers

::: machineconfig.cluster.sessions_managers.tmux.tmux_local
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Windows Terminal layout helpers

::: machineconfig.cluster.sessions_managers.windows_terminal.wt_local
    options:
      show_root_heading: true
      show_source: false
      members_order: source
