import json
import os
import pathlib


def secure_chatgpt_cli() -> None:
    config_paths = [
        "~/.config/chatgpt.json",
        "~/.config/chatgpt-cli/config.json",
        "~/.chatgpt",
        "~/.chatgpt.json",
    ]
    privacy_settings = {
        "telemetry": False,
        "analytics": False,
        "track": False,
        "cache": False,
        "save_history": False,
        "history": False,
        "data_usage": False,
        "send_usage_stats": False,
        "store": False,
        "share_data": False,
        "record": False,
    }
    for path_str in config_paths:
        path = pathlib.Path(path_str).expanduser()
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except:
                continue
        config_data = {}
        if path.exists() and path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except:
                pass
        config_data.update(privacy_settings)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            os.chmod(path, 0o600)
        except:
            pass

