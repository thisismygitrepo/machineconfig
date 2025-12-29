"""BR: Backup and Retrieve"""

# import subprocess
from collections.abc import Mapping
from machineconfig.utils.io import read_ini
from machineconfig.utils.source_of_truth import LIBRARY_ROOT, DEFAULTS_PATH
from machineconfig.utils.code import print_code
from machineconfig.utils.options import choose_cloud_interactively, choose_from_options
from machineconfig.scripts.python.helpers.helpers_cloud.helpers2 import ES
from platform import system
from typing import Literal, Optional, TypedDict
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import tomllib


OPTIONS = Literal["BACKUP", "RETRIEVE"]

LIBRARY_BACKUP_PATH = LIBRARY_ROOT.joinpath("profile/backup.toml")
USER_BACKUP_PATH = Path.home().joinpath("dotfiles/machineconfig/backup.toml")


VALID_OS = {"any", "windows", "linux", "darwin"}


class BackupItem(TypedDict):
    path_local: str
    path_remote: str | None
    zip: bool
    encrypt: bool
    rel2home: bool
    os_specific: bool
    os: set[str]


BackupConfig = dict[str, BackupItem]


def _normalize_os_name(value: str) -> str:
    return value.strip().lower()


def _parse_os_field(os_field: object, item_name: str) -> set[str]:
    if not isinstance(os_field, str) or not os_field.strip():
        raise ValueError(f"Backup entry '{item_name}' must define a non-empty 'os'.")
    token = _normalize_os_name(os_field)
    if token not in VALID_OS:
        raise ValueError(f"Backup entry '{item_name}' has an invalid 'os' value: {os_field!r}.")
    return {token}



def _os_applies(os_values: set[str], system_name: str) -> bool:
    return "any" in os_values or system_name in os_values


def _parse_bool(value: object, field: str, item_name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"Backup entry '{item_name}' has an invalid '{field}' value.")


def _require_mapping(value: object, item_name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Backup entry '{item_name}' must be a table.")
    return value


def _require_str_field(raw: Mapping[str, object], field: str, item_name: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Backup entry '{item_name}' must define a non-empty '{field}'.")
    return value.strip()


def _optional_str_field(raw: Mapping[str, object], field: str, item_name: str) -> str | None:
    if field not in raw:
        return None
    value = raw.get(field)
    if not isinstance(value, str):
        raise ValueError(f"Backup entry '{item_name}' has a non-string '{field}'.")
    token = value.strip()
    if not token:
        raise ValueError(f"Backup entry '{item_name}' has an empty '{field}'.")
    return token


def _require_bool_field(raw: Mapping[str, object], field: str, item_name: str) -> bool:
    if field not in raw:
        raise ValueError(f"Backup entry '{item_name}' must define '{field}'.")
    return _parse_bool(raw[field], field=field, item_name=item_name)


def _parse_backup_config(raw: Mapping[str, object]) -> BackupConfig:
    config: BackupConfig = {}
    for item_name, value in raw.items():
        item = _require_mapping(value, item_name)
        if "path" in item:
            raise ValueError(f"Backup entry '{item_name}' uses 'path'; use 'path_local' instead.")
        config[item_name] = {
            "path_local": _require_str_field(item, "path_local", item_name),
            "path_remote": _optional_str_field(item, "path_remote", item_name),
            "zip": _require_bool_field(item, "zip", item_name),
            "encrypt": _require_bool_field(item, "encrypt", item_name),
            "rel2home": _require_bool_field(item, "rel2home", item_name),
            "os_specific": _require_bool_field(item, "os_specific", item_name),
            "os": _parse_os_field(item.get("os"), item_name),
        }
    return config


def main_backup_retrieve(direction: OPTIONS, which: Optional[str], cloud: Optional[str]) -> None:
    console = Console()
    if cloud is None or not cloud.strip():
        try:
            cloud = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"].strip()
            console.print(Panel(f"⚠️  DEFAULT CLOUD CONFIGURATION\n🌥️  Using default cloud: {cloud}", title="[bold blue]Cloud Configuration[/bold blue]", border_style="blue"))
        except (FileNotFoundError, KeyError, IndexError):
            console.print(Panel("🔍 DEFAULT CLOUD NOT FOUND\n🔄 Please select a cloud configuration from the options below", title="[bold red]Error: Cloud Not Found[/bold red]", border_style="red"))
            cloud = choose_cloud_interactively().strip()
    else:
        cloud = cloud.strip()
        console.print(Panel(f"🌥️  Using provided cloud: {cloud}", title="[bold blue]Cloud Configuration[/bold blue]", border_style="blue"))
    assert cloud is not None
    raw_config: dict[str, object] = tomllib.loads(LIBRARY_BACKUP_PATH.read_text(encoding="utf-8"))
    bu_file = _parse_backup_config(raw_config)
    console.print(Panel(f"🧰 LOADING BACKUP CONFIGURATION\n📄 File: {LIBRARY_BACKUP_PATH}", title="[bold blue]Backup Configuration[/bold blue]", border_style="blue"))

    system_raw = system()
    normalized_system = _normalize_os_name(system_raw)
    bu_file = {
        key: val
        for key, val in bu_file.items()
        if _os_applies(val["os"], system_name=normalized_system)
    }
    console.print(Panel(
        f"🖥️  {system_raw} ENVIRONMENT DETECTED\n"
        "🔍 Filtering entries by os field\n"
        f"✅ Found {len(bu_file)} applicable backup configuration entries",
        title="[bold blue]Environment[/bold blue]",
        border_style="blue",
    ))

    if which is None:
        console.print(Panel(f"🔍 SELECT {direction} ITEMS\n📋 Choose which configuration entries to process", title="[bold blue]Select Items[/bold blue]", border_style="blue"))
        choices = choose_from_options(multi=True, msg=f"WHICH FILE of the following do you want to {direction}?", options=["all"] + list(bu_file.keys()))
    else:
        choices = which.split(",") if which else []
        console.print(Panel(f"🔖 PRE-SELECTED ITEMS\n📝 Using: {', '.join(choices)}", title="[bold blue]Pre-selected Items[/bold blue]", border_style="blue"))

    if "all" in choices:
        items = bu_file
        console.print(Panel(f"📋 PROCESSING ALL ENTRIES\n🔢 Total entries to process: {len(bu_file)}", title="[bold blue]Process All Entries[/bold blue]", border_style="blue"))
    else:
        items = {key: val for key, val in bu_file.items() if key in choices}
        console.print(Panel(f"📋 PROCESSING SELECTED ENTRIES\n🔢 Total entries to process: {len(items)}", title="[bold blue]Process Selected Entries[/bold blue]", border_style="blue"))
    program = ""
    console.print(Panel(f"🚀 GENERATING {direction} SCRIPT\n🌥️  Cloud: {cloud}\n🗂️  Items: {len(items)}", title="[bold blue]Script Generation[/bold blue]", border_style="blue"))
    for item_name, item in items.items():
        flags = ""
        flags += "z" if item["zip"] else ""
        flags += "e" if item["encrypt"] else ""
        flags += "r" if item["rel2home"] else ""
        flags += "o" if item["os_specific"] else ""
        local_path = Path(item["path_local"]).as_posix()
        if item["path_remote"] is None:
            remote_path = ES
            remote_display = f"{ES} (deduced)"
        else:
            remote_path = Path(item["path_remote"]).as_posix()
            remote_display = remote_path
        remote_spec = f"{cloud}:{remote_path}"
        console.print(Panel(
            f"📦 PROCESSING: {item_name}\n"
            f"📂 Local path: {local_path}\n"
            f"☁️  Remote path: {remote_display}\n"
            f"🏳️  Flags: {flags or 'None'}",
            title=f"[bold blue]Processing Item: {item_name}[/bold blue]",
            border_style="blue",
        ))
        flag_arg = f" -{flags}" if flags else ""
        if direction == "BACKUP":
            program += f"""\ncloud_copy "{local_path}" "{remote_spec}"{flag_arg}\n"""
        elif direction == "RETRIEVE":
            program += f"""\ncloud_copy "{remote_spec}" "{local_path}"{flag_arg}\n"""
        else:
            console.print(Panel('❌ ERROR: INVALID DIRECTION\n⚠️  Direction must be either "BACKUP" or "RETRIEVE"', title="[bold red]Error: Invalid Direction[/bold red]", border_style="red"))
            raise RuntimeError(f"Unknown direction: {direction}")
        if item_name == "dotfiles" and system_raw == "Linux":
            program += """\nchmod 700 ~/.ssh/*\n"""
            console.print(Panel("🔒 SPECIAL HANDLING: SSH PERMISSIONS\n🛠️  Setting secure permissions for SSH files\n📝 Command: chmod 700 ~/.ssh/*", title="[bold blue]Special Handling: SSH Permissions[/bold blue]", border_style="blue"))
    print_code(program, lexer="shell", desc=f"{direction} script")
    console.print(Panel(f"✅ {direction} SCRIPT GENERATION COMPLETE\n🚀 Ready to execute the operations", title="[bold green]Script Generation Complete[/bold green]", border_style="green"))
    import subprocess

    subprocess.run(program, shell=True, check=True)


if __name__ == "__main__":
    pass
