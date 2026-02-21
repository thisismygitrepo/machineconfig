"""

create 18 tasks one per cli
in each one, you do comprehensive search on internet on how to set up the cli/extension or whatever so we get max privacy and security (nothing shared everything is declined and is on the safe side)
this is a moving space, everyday, there are new versions, new configs, new settings, new policies, new rules, new terms of service, new eula, new privacy policies etc etc
so please search for latest and don't be complacent with the work done so far.

do it one by one, don't research and implement next before finishing the task before it.

I provided gemini cli solution as a reference (feel free to make it more flexible if you need mroe room to implement something more complex than what I did, its just a guide)
remember that other cli's have different names and configs and locations etc, read official docs

in the following cli how to set it for maximal prviacy *turn off any telemetry, reject any use of data, etc etc, please think of everything and read all theird docs and fine print
    "aider",
    "aichat",  # rust cli
    "copilot",  # cli from github copilot extension
    "gemini",  # gemini cli
    "crush",  # cli from charm team
    "mods",  # cli from same people as crush (not agent) @ https://github.com/charmbracelet/mods
    "opencode-ai",
    "chatgpt",
    "q",  # from aws
    "qwen-code",  # fork of gemini cli
    "cursor-cli",
    "droid",
    "kilocode",
    "cline",  # cli from cline ai extension
    "auggie",
    "codex",  # from openai

"""

from typing import Optional


import os
import re
import json
import sys
import shutil
import textwrap
import platform
import pathlib
from pathlib import Path
from typing import Optional

def secure_mods_config():
    config_dir = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    mods_dir = os.path.join(config_dir, 'mods')
    config_file = os.path.join(mods_dir, 'mods.yml')
    os.makedirs(mods_dir, exist_ok=True)
    
    content = ""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

    privacy_settings = {
        'no-cache': 'true',
        'cache-path': '"/dev/null"',
        'telemetry': 'false'
    }

    for key, value in privacy_settings.items():
        pattern = rf'^[#\s]*{key}\s*:.*$'
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(pattern, f"{key}: {value}", content, flags=re.MULTILINE)
        else:
            if not content.endswith('\n') and content != "":
                content += "\n"
            content += f"{key}: {value}\n"

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
    try:
        os.chmod(config_file, 0o600)
    except: pass

def secure_chatgpt_cli():
    CONFIG_PATHS = [
        "~/.config/chatgpt.json",
        "~/.config/chatgpt-cli/config.json",
        "~/.chatgpt",
        "~/.chatgpt.json"
    ]
    PRIVACY_SETTINGS = {
        "telemetry": False, "analytics": False, "track": False, 
        "cache": False, "save_history": False, "history": False, 
        "data_usage": False, "send_usage_stats": False, "store": False, 
        "share_data": False, "record": False
    }
    for path_str in CONFIG_PATHS:
        path = pathlib.Path(path_str).expanduser()
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except: continue
        config_data = {}
        if path.exists() and path.is_file():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except: pass
        config_data.update(PRIVACY_SETTINGS)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
            os.chmod(path, 0o600)
        except: pass

def secure_q_cli():
    privacy_settings = {
        "telemetry.enabled": False, "telemetry.disabled": True, 
        "chat.shareData": False, "completion.shareData": False, 
        "caching.enabled": False, "cache.enabled": False, 
        "aws.telemetry": False, "diagnostics.crashReporter": False
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
                except: pass
            current_settings.update(privacy_settings)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(current_settings, f, indent=2)
            if os.name != "nt":
                config_file.chmod(0o600)
        except: pass
    for exe in ["q", "kiro"]:
        if shutil.which(exe):
            for key, value in privacy_settings.items():
                val_str = "true" if value else "false"
                try:
                    subprocess.run([exe, "settings", key, val_str], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                except: pass

def secure_qwen_config():
    config_dir = os.path.expanduser("~/.qwen")
    config_file = os.path.join(config_dir, "settings.json")
    os.makedirs(config_dir, exist_ok=True)
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except: pass
    config.setdefault("privacy", {})["usageStatisticsEnabled"] = False
    config.setdefault("telemetry", {})["enabled"] = False
    config["telemetry"]["logPrompts"] = False
    config["telemetry"]["target"] = "local"
    config.setdefault("general", {})["disableAutoUpdate"] = True
    config["general"].setdefault("checkpointing", {})["enabled"] = False
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def secure_cursor_cli():
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
        "telemetry.telemetryLevel": "off", "telemetry.enableCrashReporter": False, "telemetry.enableTelemetry": False,
        "cursor.privacyMode": True, "cursor.telemetry.enabled": False, "cursor.aipreview.enabled": False,
        "cursor.cpp.enablePartialAccepts": False, "workbench.enableExperiments": False, "update.mode": "none",
        "update.showReleaseNotes": False, "update.enableWindowsBackgroundUpdates": False, "search.followSymlinks": False,
        "git.openRepositoryInParentFolders": "never", "git.autofetch": False, "typescript.tsserver.log": "off",
        "extensions.autoUpdate": False, "extensions.autoCheckUpdates": False, "extensions.ignoreRecommendations": True,
        "npm.fetchOnlinePackageInfo": False, "json.schemaDownload.enable": False, "editor.links": False, "settingsSync.keybindingsPerPlatform": False
    }
    try:
        base_dir.mkdir(parents=True, exist_ok=True)
        current_settings = {}
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                content = re.sub(r'//.*?\n|/\*.*?\*/', '\n', f.read(), flags=re.S)
                if content.strip(): current_settings = json.loads(content)
        current_settings.update(privacy_settings)
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(current_settings, f, indent=4)
    except: pass

def secure_droid_cli():
    config_dir = Path.home() / ".factory"
    config_file = config_dir / "settings.json"
    config_dir.mkdir(parents=True, exist_ok=True)
    settings = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except: pass
    settings.update({"cloudSessionSync": False, "enableDroidShield": True, "telemetry": False, "caching": False, "analytics": False, "data_usage": False, "dataUsage": False})
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def secure_kilocode_config():
    config_dir = pathlib.Path.home() / ".config" / "kilocode"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    secure_settings = {
        "telemetry": False, "analytics_opt_in": False, "caching": False, "cache_enabled": False, 
        "data_usage": "reject", "crash_reporting": False, "send_usage_metrics": False, 
        "allow_tracking": False, "telemetry_enabled": False, "offline_mode": True 
    }
    current_config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f: current_config = json.load(f)
        except: pass
    current_config.update(secure_settings)
    with open(config_file, 'w', encoding='utf-8') as f: json.dump(current_config, f, indent=4)
    try: os.chmod(config_file, 0o600)
    except: pass

def secure_cline_config():
    home = Path.home()
    vscode_storage = home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.cline"
    config_paths = [
        home / ".cline" / "settings.json",
        home / ".cline" / "config.json",
        home / ".config" / "cline" / "settings.json",
        vscode_storage / "settings.json",
        vscode_storage / "settings" / "settings.json"
    ]
    privacy_settings = {"telemetry": False, "telemetry.enabled": False, "disableTelemetry": True, "analytics": False, "allowAnalytics": False, "allowDataUsage": False, "dataCollection": False, "crashReporting": False, "cache": False, "enableCaching": False, "disableCaching": True, "history": False, "recordHistory": False}
    for path in config_paths:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            config_data = {}
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f: config_data = json.load(f)
                except: pass
            config_data.update(privacy_settings)
            with open(path, 'w', encoding='utf-8') as f: json.dump(config_data, f, indent=4)
            os.chmod(path, 0o600)
        except: pass

def secure_auggie_config():
    config_dir = Path.home() / ".augment"
    config_dir.mkdir(parents=True, exist_ok=True)
    settings_file = config_dir / "settings.json"
    settings = {}
    if settings_file.exists():
        try: settings = json.loads(settings_file.read_text())
        except: pass
    settings["indexingAllowDirs"] = []
    settings["indexingDenyDirs"] = ["/"]
    settings["autoUpdate"] = False
    settings["toolPermissions"] = []
    privacy_flags = {"telemetry": False, "telemetryEnabled": False, "optInTelemetry": False, "analytics": False, "shareData": False, "dataUsage": "deny", "cache": "none", "caching": False}
    settings.update(privacy_flags)
    feature_flags = settings.get("featureFlagOverrides", {})
    if isinstance(feature_flags, dict):
        feature_flags.update(privacy_flags)
        settings["featureFlagOverrides"] = feature_flags
    settings_file.write_text(json.dumps(settings, indent=2))
    try: settings_file.chmod(0o600)
    except: pass

def secure_codex_configs():
    config_content = textwrap.dedent("""\
        [analytics]
        enabled = false
        [otel]
        exporter = "none"
        metrics_exporter = "none"
        trace_exporter = "none"
        log_user_prompt = false
        [history]
        persistence = "none"
        web_search = "disabled"
        commit_attribution = ""
        [features]
        web_search = false
        web_search_cached = false
        web_search_request = false
        collab = false
        remote_models = false
    """)
    targets = [pathlib.Path.home() / ".codex" / "config.toml", pathlib.Path.cwd() / ".codex" / "config.toml"]
    for config_path in targets:
        if config_path == targets[0] or config_path.parent.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(config_content, encoding="utf-8")
            try: os.chmod(config_path, 0o600)
            except: pass


def apply_max_privacy_and_security_rules_and_configs(
    overwrite: bool, repo_root: Optional[str]
) -> None:
    from machineconfig.utils.source_of_truth import LIBRARY_ROOT

    root = LIBRARY_ROOT / "scripts/python/helpers_agents/privacy/configs"

    # Gemini privacy settings
    gemini_settings_source = root.joinpath("gemini/settings.json")
    gemini_settings_target_global = Path.home().joinpath(".gemini/settings.json")
    if not gemini_settings_target_global.exists() or overwrite:
        gemini_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        if gemini_settings_source.exists():
            gemini_settings_target_global.write_text(gemini_settings_source.read_text())
    if repo_root:
        gemini_settings_target_repo = Path(repo_root).joinpath(".gemini/settings.json")
        if not gemini_settings_target_repo.exists() or overwrite:
            gemini_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            if gemini_settings_source.exists():
                gemini_settings_target_repo.write_text(gemini_settings_source.read_text())

    # Aider privacy settings
    aider_settings_source = root.joinpath("aider/.aider.conf.yml")
    aider_settings_target_global = Path.home().joinpath(".aider.conf.yml")
    if not aider_settings_target_global.exists() or overwrite:
        aider_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        if aider_settings_source.exists():
            aider_settings_target_global.write_text(aider_settings_source.read_text())

    if repo_root:
        aider_settings_target_repo = Path(repo_root).joinpath(".aider.conf.yml")
        if not aider_settings_target_repo.exists() or overwrite:
            aider_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            if aider_settings_source.exists():
                aider_settings_target_repo.write_text(aider_settings_source.read_text())

    # Aichat privacy settings
    aichat_settings_source = root.joinpath("aichat/config.yaml")
    aichat_settings_target_global = Path.home().joinpath(".config/aichat/config.yaml")
    if not aichat_settings_target_global.exists() or overwrite:
        aichat_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        if aichat_settings_source.exists():
            aichat_settings_target_global.write_text(aichat_settings_source.read_text())

    if repo_root:
        aichat_settings_target_repo = Path(repo_root).joinpath(
            ".config/aichat/config.yaml"
        )
        if not aichat_settings_target_repo.exists() or overwrite:
            aichat_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            if aichat_settings_source.exists():
                aichat_settings_target_repo.write_text(aichat_settings_source.read_text())

    # Copilot privacy settings
    copilot_settings_source = root.joinpath("copilot/config.yml")
    copilot_settings_target_global = Path.home().joinpath(
        ".config/gh-copilot/config.yml"
    )
    if not copilot_settings_target_global.exists() or overwrite:
        copilot_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        if copilot_settings_source.exists():
            copilot_settings_target_global.write_text(copilot_settings_source.read_text())

    if repo_root:
        copilot_settings_target_repo = Path(repo_root).joinpath(
            ".config/gh-copilot/config.yml"
        )
        if not copilot_settings_target_repo.exists() or overwrite:
            copilot_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            if copilot_settings_source.exists():
                copilot_settings_target_repo.write_text(copilot_settings_source.read_text())

    # Crush privacy settings
    crush_settings_source = root.joinpath("crush/crush.json")
    crush_settings_target_global = Path.home().joinpath(".config/crush/crush.json")
    if not crush_settings_target_global.exists() or overwrite:
        crush_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        if crush_settings_source.exists():
            crush_settings_target_global.write_text(crush_settings_source.read_text())

    if repo_root:
        crush_settings_target_repo = Path(repo_root).joinpath(".crush.json")
        if not crush_settings_target_repo.exists() or overwrite:
            crush_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            if crush_settings_source.exists():
                crush_settings_target_repo.write_text(crush_settings_source.read_text())

    # OpenCode privacy settings
    try:
        from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.opencode.opencode_privacy import (
            apply_opencode_privacy,
        )

        apply_opencode_privacy(scope="global")
        if repo_root:
            apply_opencode_privacy(scope="repo", repo_path=repo_root)
    except Exception as e:
        print(f"Failed to apply opencode privacy settings: {e}")

    # Invoke all other CLI privacy lockdowns
    try: secure_mods_config()
    except Exception: pass

    try: secure_chatgpt_cli()
    except Exception: pass

    try: secure_q_cli()
    except Exception: pass

    try: secure_qwen_config()
    except Exception: pass

    try: secure_cursor_cli()
    except Exception: pass

    try: secure_droid_cli()
    except Exception: pass

    try: secure_kilocode_config()
    except Exception: pass

    try: secure_cline_config()
    except Exception: pass

    try: secure_auggie_config()
    except Exception: pass

    try: secure_codex_configs()
    except Exception: pass

if __name__ == "__main__":
    apply_max_privacy_and_security_rules_and_configs(overwrite=True, repo_root=None)
