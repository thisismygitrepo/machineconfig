import json
import platform
import re
from pathlib import Path


def secure_cursor_cli() -> None:
    system = platform.system()
    home = Path.home()
    if system == "Windows":
        base_dir = home / "AppData" / "Roaming" / "Cursor" / "User"
    elif system == "Darwin":
        base_dir = home / "Library" / "Application Support" / "Cursor" / "User"
    else:
        base_dir = home / ".config" / "Cursor" / "User"
    settings_file = base_dir / "settings.json"
    privacy_settings = {
        "telemetry.telemetryLevel": "off",
        "telemetry.enableCrashReporter": False,
        "telemetry.enableTelemetry": False,
        "cursor.privacyMode": True,
        "cursor.telemetry.enabled": False,
        "cursor.aipreview.enabled": False,
        "cursor.cpp.enablePartialAccepts": False,
        "workbench.enableExperiments": False,
        "update.mode": "none",
        "update.showReleaseNotes": False,
        "update.enableWindowsBackgroundUpdates": False,
        "search.followSymlinks": False,
        "git.openRepositoryInParentFolders": "never",
        "git.autofetch": False,
        "typescript.tsserver.log": "off",
        "extensions.autoUpdate": False,
        "extensions.autoCheckUpdates": False,
        "extensions.ignoreRecommendations": True,
        "npm.fetchOnlinePackageInfo": False,
        "json.schemaDownload.enable": False,
        "editor.links": False,
        "settingsSync.keybindingsPerPlatform": False,
    }
    try:
        base_dir.mkdir(parents=True, exist_ok=True)
        current_settings = {}
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                content = re.sub(r"//.*?\n|/\*.*?\*/", "\n", f.read(), flags=re.S)
                if content.strip():
                    current_settings = json.loads(content)
        current_settings.update(privacy_settings)
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(current_settings, f, indent=4)
    except:
        pass

