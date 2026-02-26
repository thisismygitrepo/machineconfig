from pathlib import Path
import textwrap

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def _build_private_config() -> str:
    return textwrap.dedent(
        """\
        approval_policy = "never"
        sandbox_mode = "workspace-write"
        allow_login_shell = false
        web_search = "enabled"
        project_doc_max_bytes = 32768
        project_doc_fallback_filenames = []
        mcp_oauth_credentials_store = "auto"

        [sandbox_workspace_write]
        network_access = true

        [features]
        multi_agent = true
        remote_models = true

        [analytics]
        enabled = false

        [history]
        persistence = "none"

        [feedback]
        enabled = false

        [otel]
        log_user_prompt = false
        exporter = "none"
        trace_exporter = "none"

        [mcp_servers]
        """
    )


def _ensure_private_config(repo_root: Path) -> None:
    codex_dir = repo_root.joinpath(".codex")
    codex_dir.mkdir(parents=True, exist_ok=True)
    config_path = codex_dir.joinpath("config.toml")
    if config_path.exists():
        return
    config_path.write_text(data=_build_private_config(), encoding="utf-8")


def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    if add_private_config:
        _ensure_private_config(repo_root=repo_root)

    if add_instructions:
        instructions_path = get_generic_instructions_path()
        repo_root.joinpath("AGENTS.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
