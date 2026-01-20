from pathlib import Path


def check_cloud_init_overrides() -> tuple[list[Path], dict[str, tuple[Path, str]]]:
    sshd_config_d = Path("/etc/ssh/sshd_config.d")
    override_files: list[Path] = []
    auth_overrides: dict[str, tuple[Path, str]] = {}
    if not sshd_config_d.exists():
        return override_files, auth_overrides
    for conf_file in sorted(sshd_config_d.glob("*.conf")):
        override_files.append(conf_file)
        try:
            conf_text = conf_file.read_text(encoding="utf-8")
            for line in conf_text.split("\n"):
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith("#"):
                    parts = line_stripped.split(None, 1)
                    if len(parts) >= 2:
                        key, value = parts[0], parts[1]
                        if key in ("PasswordAuthentication", "PubkeyAuthentication", "PermitRootLogin", "ChallengeResponseAuthentication", "KbdInteractiveAuthentication"):
                            auth_overrides[key] = (conf_file, value.lower())
        except Exception:
            pass
    return override_files, auth_overrides


def generate_cloud_init_fix_script(auth_overrides: dict[str, tuple[Path, str]]) -> str:
    fix_commands: list[str] = []
    for key, (file_path, value) in auth_overrides.items():
        if key in ("PasswordAuthentication", "PubkeyAuthentication") and value == "no":
            fix_commands.append(f"# Fix {key} in {file_path.name}")
            fix_commands.append(f"sudo sed -i 's/^{key}.*no/{key} yes/' {file_path}")
    return "\n".join(fix_commands)
