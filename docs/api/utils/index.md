# Utils API

`machineconfig.utils` is the shared-library layer that most downstream code imports directly. It contains environment discovery, IO and path helpers, schedulers and caches, interactive selection utilities, notification helpers, and the script-generation functions that feed the cluster and installer layers.

---

## Topics in this section

| Topic | Use it when you need to... | Main modules |
| --- | --- | --- |
| [Environment and project wiring](environment-and-projects.md) | Discover project virtualenvs, optional IPython profiles, and `.ve.yaml` cloud metadata | `machineconfig.utils.ve` |
| [Paths, files, and config](paths-files-config.md) | Read and write JSON / INI / pickle files, encrypt files with GPG, resolve paths and path references | `machineconfig.utils.io`, `machineconfig.utils.path_core`, `machineconfig.utils.path_helper`, `machineconfig.utils.path_reference` |
| [Scheduling and cache](scheduling-and-cache.md) | Run recurring routines and reuse expensive results through memory or disk caches | `machineconfig.utils.scheduler` |
| [Interactive helpers and notifications](interactive-helpers.md) | Generate IDs, split work, present interactive choices, and send email | `machineconfig.utils.accessories`, `machineconfig.utils.options`, `machineconfig.utils.notifications` |
| [Code generation and command launching](code-generation.md) | Turn callables into scripts, build `uv` commands, run shell snippets, and ensure CLIs exist | `machineconfig.utils.meta`, `machineconfig.utils.code`, `machineconfig.utils.installer_utils.installer_cli` |

---

## What tends to live outside this section

- Layout schemas and terminal-session backends are documented under [Cluster](../cluster/index.md), even though they depend on several utils modules.
- `machineconfig.utils.ssh` is documented from [Remote execution and networking](../cluster/remote.md) because it is usually consumed as part of a remote workflow.
- Installer data and package groups live under [Jobs](../jobs/index.md), while the runtime installer engine lives under `machineconfig.utils.installer_utils`.

---

## Typical import patterns

```python
from machineconfig.utils.accessories import randstr, split_list
from machineconfig.utils.code import run_shell_script
from machineconfig.utils.io import read_json, save_json
from machineconfig.utils.options import choose_from_options
from machineconfig.utils.path_core import collapseuser, tmpfile
from machineconfig.utils.scheduler import Scheduler, CacheMemory
from machineconfig.utils.ve import get_ve_path_and_ipython_profile
```

The utilities in this section are intentionally low-level. Higher-level session, cluster, and installer flows mostly build on these primitives rather than replacing them.
