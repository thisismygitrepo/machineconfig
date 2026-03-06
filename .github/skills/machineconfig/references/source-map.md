# Machineconfig Source Map

Use this map to jump from a direct CLI command path to the file that registers it and where behavior is implemented.

## Direct App Modules

- `devops ...`
  - Group registration: `src/machineconfig/scripts/python/devops.py`
  - Nested apps:
    - `repos` -> `src/machineconfig/scripts/python/helpers/helpers_devops/cli_repos.py`
    - `config` -> `src/machineconfig/scripts/python/helpers/helpers_devops/cli_config.py`
    - `data` -> `src/machineconfig/scripts/python/helpers/helpers_devops/cli_data.py`
    - `self` -> `src/machineconfig/scripts/python/helpers/helpers_devops/cli_self.py`
    - `network` -> `src/machineconfig/scripts/python/helpers/helpers_devops/cli_nw.py`

- `cloud ...`
  - Group registration: `src/machineconfig/scripts/python/cloud.py`
  - Helper implementations:
    - `sync` -> `helpers/helpers_cloud/cloud_sync.py`
    - `copy` -> `helpers/helpers_cloud/cloud_copy.py`
    - `mount` -> `helpers/helpers_cloud/cloud_mount.py`
    - `ftpx` -> `src/machineconfig/scripts/python/ftpx.py` -> `helpers/helpers_network/ftpx_impl.py`

- `sessions ...`
  - Group registration: `src/machineconfig/scripts/python/sessions.py`
  - Heavy logic in `helpers/helpers_sessions/*`

- `agents ...`
  - Group registration: `src/machineconfig/scripts/python/agents.py`
  - Heavy logic in `helpers/helpers_agents/*` and `scripts/python/ai/utils/*`

- `utils ...`
  - Group registration: `src/machineconfig/scripts/python/utils.py`
  - Implementations spread across `helpers/helpers_utils/*`, `machineconfig/utils/*`, and `machineconfig/type_hinting/*`

- `fire ...`
  - Registration and CLI surface: `src/machineconfig/scripts/python/fire_jobs.py`
  - Core helpers: `helpers/helpers_fire_command/fire_jobs_args_helper.py`, `helpers/helpers_fire_command/fire_jobs_impl.py`

- `croshell ...`
  - Registration and CLI surface: `src/machineconfig/scripts/python/croshell.py`
  - Helper backend routing: `helpers/helpers_croshell/croshell_impl.py`

- `msearch ...`
  - Registration and CLI surface: `src/machineconfig/scripts/python/msearch.py`
  - Helper implementation: `helpers/helpers_msearch/msearch_impl.py`

## Nested Group Apps

- `devops network ssh ...`
  - Registration: `src/machineconfig/scripts/python/helpers/helpers_devops/cli_ssh.py`

- `devops self explore ...`
  - Registration: `src/machineconfig/scripts/python/graph/visualize/cli_graph_app.py`

- `devops self security ...`
  - Registration: `src/machineconfig/jobs/installer/checks/security_cli.py`

## Debugging and Validation Workflow

1. Confirm command registration path in the appropriate `get_app()` file.
2. Trace imported implementation module from the command function body.
3. Validate help surface locally:
   - `UV_CACHE_DIR=/tmp/uv-cache uv run devops --help`
   - `UV_CACHE_DIR=/tmp/uv-cache uv run devops repos --help`
4. If adding/changing command names, update:
   - Typer registration(s)
   - callable signature/help text
   - any wrappers or docs that reference old paths
