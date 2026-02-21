import json
from pathlib import Path


def secure_droid_cli() -> None:
    config_dir = Path.home() / ".factory"
    config_file = config_dir / "settings.json"
    config_dir.mkdir(parents=True, exist_ok=True)

    settings = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except:
            pass
    settings.update(
        {
            "cloudSessionSync": False,
            "enableDroidShield": True,
            "telemetry": False,
            "caching": False,
            "analytics": False,
            "data_usage": False,
            "dataUsage": False,
        }
    )
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

