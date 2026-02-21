import json
import os
from pathlib import Path


def secure_cline_config() -> None:
    home = Path.home()
    vscode_storage = home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.cline"
    config_paths = [
        home / ".cline" / "settings.json",
        home / ".cline" / "config.json",
        home / ".config" / "cline" / "settings.json",
        vscode_storage / "settings.json",
        vscode_storage / "settings" / "settings.json",
    ]
    privacy_settings = {
        "telemetry": False,
        "telemetry.enabled": False,
        "disableTelemetry": True,
        "analytics": False,
        "allowAnalytics": False,
        "allowDataUsage": False,
        "dataCollection": False,
        "crashReporting": False,
        "cache": False,
        "enableCaching": False,
        "disableCaching": True,
        "history": False,
        "recordHistory": False,
    }
    for path in config_paths:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            config_data = {}
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                except:
                    pass
            config_data.update(privacy_settings)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            os.chmod(path, 0o600)
        except:
            pass

