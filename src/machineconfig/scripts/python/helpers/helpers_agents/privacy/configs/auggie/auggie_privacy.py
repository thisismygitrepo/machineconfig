import json
from pathlib import Path


def secure_auggie_config() -> None:
    config_dir = Path.home() / ".augment"
    config_dir.mkdir(parents=True, exist_ok=True)
    settings_file = config_dir / "settings.json"
    settings = {}
    if settings_file.exists():
        try:
            settings = json.loads(settings_file.read_text())
        except:
            pass
    settings["indexingAllowDirs"] = []
    settings["indexingDenyDirs"] = ["/"]
    settings["autoUpdate"] = False
    settings["toolPermissions"] = []
    privacy_flags = {
        "telemetry": False,
        "telemetryEnabled": False,
        "optInTelemetry": False,
        "analytics": False,
        "shareData": False,
        "dataUsage": "deny",
        "cache": "none",
        "caching": False,
    }
    settings.update(privacy_flags)
    feature_flags = settings.get("featureFlagOverrides", {})
    if isinstance(feature_flags, dict):
        feature_flags.update(privacy_flags)
        settings["featureFlagOverrides"] = feature_flags
    settings_file.write_text(json.dumps(settings, indent=2))
    try:
        settings_file.chmod(0o600)
    except:
        pass

