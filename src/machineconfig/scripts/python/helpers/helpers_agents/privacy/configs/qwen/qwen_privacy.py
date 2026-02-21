import json
import os


def secure_qwen_config() -> None:
    config_dir = os.path.expanduser("~/.qwen")
    config_file = os.path.join(config_dir, "settings.json")
    os.makedirs(config_dir, exist_ok=True)

    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except:
            pass
    config.setdefault("privacy", {})["usageStatisticsEnabled"] = False
    config.setdefault("telemetry", {})["enabled"] = False
    config["telemetry"]["logPrompts"] = False
    config["telemetry"]["target"] = "local"
    config.setdefault("general", {})["disableAutoUpdate"] = True
    config["general"].setdefault("checkpointing", {})["enabled"] = False

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

