import json
import os
import shutil
import subprocess
from pathlib import Path


def secure_q_cli() -> None:
    privacy_settings = {
        "telemetry.enabled": False,
        "telemetry.disabled": True,
        "chat.shareData": False,
        "completion.shareData": False,
        "caching.enabled": False,
        "cache.enabled": False,
        "aws.telemetry": False,
        "diagnostics.crashReporter": False,
    }
    home = Path.home()
    config_paths = [
        home / ".config" / "amazon-q" / "settings.json",
        home / ".amazon-q" / "settings.json",
        home / ".aws" / "amazon-q" / "settings.json",
        home / ".config" / "kiro" / "settings.json",
        home / ".kiro" / "settings.json",
    ]
    for config_file in config_paths:
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            current_settings = {}
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        current_settings = json.load(f)
                except:
                    pass
            current_settings.update(privacy_settings)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(current_settings, f, indent=2)
            if os.name != "nt":
                config_file.chmod(0o600)
        except:
            pass
    for exe in ["q", "kiro"]:
        if shutil.which(exe):
            for key, value in privacy_settings.items():
                val_str = "true" if value else "false"
                try:
                    subprocess.run(
                        [exe, "settings", key, val_str],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                except:
                    pass

