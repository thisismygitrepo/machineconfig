# Environment and Project Wiring

The environment helpers in `machineconfig` live in `machineconfig.utils.ve`. They answer two practical questions:

- which virtualenv should this project use?
- does the project declare an IPython profile or cloud-sync metadata in `.ve.yaml`?

---

## What this layer provides

| API | Responsibility |
| --- | --- |
| `FILE_NAME` | The project-level config file name: `.ve.yaml` |
| `CLOUD` | Typed cloud metadata for keys such as `cloud`, `root`, `encrypt`, `share`, and `overwrite` |
| `VE_SPECS` | Typed `specs` block containing `ve_path` and optional `ipy_profile` |
| `VE_YAML` | Typed top-level structure for `.ve.yaml` |
| `read_default_cloud_config()` | Returns the default `CLOUD` payload used by callers as a baseline |
| `get_ve_path_and_ipython_profile(init_path)` | Walks upward from a path and resolves virtualenv plus optional IPython profile |
| `get_ve_activate_line(ve_root)` | Builds the platform-specific shell line that activates a virtualenv |

---

## Discovery model

`get_ve_path_and_ipython_profile(init_path)` walks through `init_path` and its parents.

At each directory it:

1. Reads `.ve.yaml` if present.
2. Pulls `specs.ve_path` into the result when available.
3. Pulls `specs.ipy_profile` into the result when available.
4. Falls back to a local `.venv` directory only if no `ve_path` has been found yet.

The walk stops as soon as both values are known, otherwise it continues to the filesystem root. The function returns a tuple of `(ve_path, ipy_profile)` where either element may be `None`. It also prints progress and warning messages while it searches.

---

## Example `.ve.yaml`

```yaml
specs:
  ve_path: ~/.venvs/my-project
  ipy_profile: default

cloud:
  cloud: mycloud101
  root: myhome
  rel2home: false
  pwd: null
  key: null
  encrypt: false
  os_specific: false
  zip: false
  share: false
  overwrite: false
```

The `cloud` section is typed by `CLOUD` and is available to callers that want lightweight per-project sync metadata. Environment discovery itself only needs the `specs` block.

---

## Activation lines

`get_ve_activate_line(ve_root)` returns:

- `. {ve_root}/bin/activate` on Linux and macOS
- `. $HOME/<relative-path>/Scripts/activate.ps1` on Windows

The Windows branch rewrites the expanded virtualenv path to a `$HOME/.../Scripts/activate.ps1` PowerShell source line.

---

## Example usage

```python
from pathlib import Path

from machineconfig.utils.ve import (
    FILE_NAME,
    get_ve_activate_line,
    get_ve_path_and_ipython_profile,
)

project_path = Path.cwd()
ve_path, ipy_profile = get_ve_path_and_ipython_profile(project_path)

print(FILE_NAME)
print(ve_path)
print(ipy_profile)

if ve_path is not None:
    print(get_ve_activate_line(ve_path))
```

---

## API reference

::: machineconfig.utils.ve
    options:
      show_root_heading: true
      show_source: false
      members_order: source
