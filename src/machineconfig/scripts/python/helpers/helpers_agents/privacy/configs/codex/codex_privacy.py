import os
import pathlib
import textwrap


def secure_codex_configs() -> None:
    config_content = textwrap.dedent(
        """

        [analytics]
        enabled = false
        [otel]
        exporter = "none"
        metrics_exporter = "none"
        trace_exporter = "none"
        log_user_prompt = false
        [history]
        persistence = "none"
        commit_attribution = ""
        [features]
        multi_agent = true
        remote_models = true
    """
    )
    targets = [pathlib.Path.home() / ".codex" / "config.toml", pathlib.Path.cwd() / ".codex" / "config.toml"]
    for config_path in targets:
        if config_path == targets[0] or config_path.parent.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(config_content, encoding="utf-8")
            try:
                os.chmod(config_path, 0o600)
            except:
                pass
