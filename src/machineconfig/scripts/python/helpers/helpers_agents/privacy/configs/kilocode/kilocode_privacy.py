import json
import os
import pathlib


def secure_kilocode_config() -> None:
    config_dir = pathlib.Path.home() / ".config" / "kilocode"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    secure_settings = {
        "telemetry": False,
        "analytics_opt_in": False,
        "caching": False,
        "cache_enabled": False,
        "data_usage": "reject",
        "crash_reporting": False,
        "send_usage_metrics": False,
        "allow_tracking": False,
        "telemetry_enabled": False,
        "offline_mode": True,
    }
    current_config = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                current_config = json.load(f)
        except:
            pass
    current_config.update(secure_settings)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(current_config, f, indent=4)
    try:
        os.chmod(config_file, 0o600)
    except:
        pass

