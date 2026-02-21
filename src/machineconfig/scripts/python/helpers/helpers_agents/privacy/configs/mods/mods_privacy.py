import os
import re


def secure_mods_config() -> None:
    config_dir = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    mods_dir = os.path.join(config_dir, "mods")
    config_file = os.path.join(mods_dir, "mods.yml")
    os.makedirs(mods_dir, exist_ok=True)

    content = ""
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()

    privacy_settings = {
        "no-cache": "true",
        "cache-path": '"/dev/null"',
        "telemetry": "false",
    }

    for key, value in privacy_settings.items():
        pattern = rf"^[#\s]*{key}\s*:.*$"
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(pattern, f"{key}: {value}", content, flags=re.MULTILINE)
        else:
            if not content.endswith("\n") and content != "":
                content += "\n"
            content += f"{key}: {value}\n"

    with open(config_file, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    try:
        os.chmod(config_file, 0o600)
    except:
        pass

