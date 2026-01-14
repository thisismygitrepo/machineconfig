"""BR: Backup and Retrieve"""

import re
from platform import system
from typing import Literal, Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from machineconfig.utils.io import read_ini
from machineconfig.utils.source_of_truth import DEFAULTS_PATH
from machineconfig.utils.code import print_code
from machineconfig.utils.options import choose_cloud_interactively
from machineconfig.scripts.python.helpers.helpers_cloud.helpers2 import ES
from machineconfig.scripts.python.helpers.helpers_devops.backup_config import (
    BackupConfig, BackupGroup, VALID_OS, USER_BACKUP_PATH, DEFAULT_BACKUP_HEADER,
    normalize_os_name, os_applies, read_backup_config,
)
from machineconfig.profile.create_links_export import REPO_LOOSE

DIRECTION = Literal["BACKUP", "RETRIEVE"]


def _sanitize_entry_name(value: str) -> str:
    token = value.strip().replace(".", "_").replace("-", "_")
    token = re.sub(r"\s+", "_", token)
    token = re.sub(r"[^A-Za-z0-9_]", "_", token)
    return token or "backup_item"


def _format_backup_entry_block(
    entry_name: str,
    path_local: str,
    path_cloud: str,
    zip: bool,
    encrypt: bool,
    rel2home: bool,
    os_value: str,
) -> str:
    parts = [
        f"path_local = '{path_local}'",
        f"path_cloud = '{path_cloud}'",
        f"encrypt = {str(encrypt).lower()}",
        f"zip = {str(zip).lower()}",
        f"rel2home = {str(rel2home).lower()}",
        f"os = '{os_value}'",
    ]
    return f"{entry_name} = {{ {', '.join(parts)} }}"


def _upsert_backup_entry(content: str, group_name: str, entry_name: str, entry_line: str) -> tuple[str, bool]:
    header = f"[{group_name}]"
    lines = content.splitlines()
    new_lines: list[str] = []
    in_target = False
    entry_written = False
    replaced = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_target and not entry_written:
                new_lines.append(entry_line)
                entry_written = True
            in_target = False
            if stripped == header:
                in_target = True
            new_lines.append(line)
            continue
        if in_target:
            if stripped.startswith(f"{entry_name} ="):
                new_lines.append(entry_line)
                replaced = True
                entry_written = True
                continue
        new_lines.append(line)
    if not entry_written:
        if header not in content:
            if new_lines and new_lines[-1].strip():
                new_lines.append("")
            new_lines.append(header)
        new_lines.append(entry_line)
    updated = "\n".join(new_lines).rstrip() + "\n"
    return updated, replaced


def register_backup_entry(
    path_local: str,
    group: str,
    entry_name: Optional[str] = None,
    path_cloud: Optional[str] = None,
    zip: bool = True,
    encrypt: bool = True,
    rel2home: Optional[bool] = None,
    os: str = "any",
) -> tuple[Path, str, bool]:
    local_path = Path(path_local).expanduser().absolute()
    if not local_path.exists():
        raise ValueError(f"Local path does not exist: {local_path}")
    os_parts = [part.strip() for part in os.split(",")]
    os_tokens: list[str] = []
    for part in os_parts:
        if not part:
            continue
        token = normalize_os_name(part)
        if token in {"any", "all", "*"}:
            os_tokens = ["any"]
            break
        if token not in VALID_OS:
            raise ValueError(f"Invalid os value: {os!r}. Expected one of: {sorted(VALID_OS)}")
        os_tokens.append(token)
    if not os_tokens:
        raise ValueError(f"Invalid os value: {os!r}. Expected one of: {sorted(VALID_OS)}")
    home = Path.home()
    in_home = local_path.is_relative_to(home)
    if rel2home is None:
        rel2home = in_home
    if rel2home and not in_home:
        raise ValueError("rel2home is true, but the local path is not under the home directory.")
    group_name = _sanitize_entry_name(group) if group and group.strip() else "default"
    if entry_name is None or not entry_name.strip():
        base_name = _sanitize_entry_name(local_path.stem)
        os_tag = "any" if "any" in os_tokens else "_".join(os_tokens)
        entry_name = f"{base_name}_{os_tag}" if os_tag != "any" else base_name
    else:
        entry_name = _sanitize_entry_name(entry_name)
    local_display = f"~/{local_path.relative_to(home)}" if rel2home and in_home else local_path.as_posix()
    cloud_value = path_cloud.strip() if path_cloud and path_cloud.strip() else ES
    os_value = "any" if "any" in os_tokens else ",".join(os_tokens)
    entry_block = _format_backup_entry_block(
        entry_name=entry_name,
        path_local=local_display,
        path_cloud=cloud_value,
        zip=zip,
        encrypt=encrypt,
        rel2home=rel2home,
        os_value=os_value,
    )
    USER_BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    if USER_BACKUP_PATH.exists():
        content = USER_BACKUP_PATH.read_text(encoding="utf-8")
    else:
        content = DEFAULT_BACKUP_HEADER
    updated, replaced = _upsert_backup_entry(content=content, group_name=group_name, entry_name=entry_name, entry_line=entry_block)
    USER_BACKUP_PATH.write_text(updated, encoding="utf-8")
    return USER_BACKUP_PATH, entry_name, replaced


def main_backup_retrieve(direction: DIRECTION, which: Optional[str], cloud: Optional[str], repo: REPO_LOOSE) -> None:
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
    bu_file: BackupConfig = read_backup_config(repo=repo)
    system_raw = system()
    normalized_system = normalize_os_name(system_raw)
    filtered: BackupConfig = {}
    for group_name, group_items in bu_file.items():
        matched: BackupGroup = {}
        for key, val in group_items.items():
            if os_applies(val["os"], system_name=normalized_system):
                matched[key] = val
        if matched:
            filtered[group_name] = matched
    bu_file = filtered
    console.print(Panel(
        f"🖥️  {system_raw} ENVIRONMENT DETECTED\n"
        "🔍 Filtering entries by os field\n"
        f"✅ Found {sum(len(item) for item in bu_file.values())} applicable backup configuration entries",
        title="[bold blue]Environment[/bold blue]",
        border_style="blue",
    ))

    if which is None:
        # import platform
        # if platform.system() not in {"Linux", "Darwin"}:
        #     console.print(Panel(f"🔍 SELECT {direction} ITEMS\n📋 Choose which configuration entries to process", title="[bold blue]Select Items[/bold blue]", border_style="blue"))
        #     choices = choose_from_options(multi=True, msg=f"WHICH FILE of the following do you want to {direction}?", options=["all"] + list(bu_file.keys()), tv=True)
        # else:
        from machineconfig.utils.options_utils.options_tv_linux import select_from_options
        choice = select_from_options(
            options_to_preview_mapping=bu_file, extension="toml", multi=False, preview_size_percent=75.0,
        )
        if choice is None:
            console.print(Panel("❌ NO ITEMS SELECTED\n⚠️  Exiting without processing any items", title="[bold red]No Items Selected[/bold red]", border_style="red"))
            return
        choices = [choice]
    else:
        choices = [token.strip() for token in which.split(",")] if which else []
        console.print(Panel(f"🔖 PRE-SELECTED ITEMS\n📝 Using: {', '.join(choices)}", title="[bold blue]Pre-selected Items[/bold blue]", border_style="blue"))

    items: BackupConfig
    if "all" in choices:
        items = bu_file
        console.print(Panel(f"📋 PROCESSING ALL ENTRIES\n🔢 Total entries to process: {sum(len(item) for item in bu_file.values())}", title="[bold blue]Process All Entries[/bold blue]", border_style="blue"))
    else:
        items = {}
        unknown: list[str] = []
        for choice in choices:
            if not choice:
                continue
            if choice in bu_file:
                items[choice] = bu_file[choice]
                continue
            if "." in choice:
                group_name, item_name = choice.split(".", 1)
                if group_name in bu_file and item_name in bu_file[group_name]:
                    items.setdefault(group_name, {})[item_name] = bu_file[group_name][item_name]
                    continue
            unknown.append(choice)
        if unknown:
            raise ValueError(f"Unknown backup entries: {', '.join(unknown)}")
        console.print(Panel(f"📋 PROCESSING SELECTED ENTRIES\n🔢 Total entries to process: {sum(len(item) for item in items.values())}", title="[bold blue]Process Selected Entries[/bold blue]", border_style="blue"))
    program = ""
    console.print(Panel(f"🚀 GENERATING {direction} SCRIPT\n🌥️  Cloud: {cloud}\n🗂️  Items: {sum(len(item) for item in items.values())}", title="[bold blue]Script Generation[/bold blue]", border_style="blue"))
    for group_name, group_items in items.items():
        for item_name, item in group_items.items():
            display_name = f"{group_name}.{item_name}"
            flags = ""
            flags += "z" if item["zip"] else ""
            flags += "e" if item["encrypt"] else ""
            flags += "r" if item["rel2home"] else ""
            flags += "o" if "any" not in item["os"] else ""
            local_path = Path(item["path_local"]).as_posix()
            if item["path_cloud"] in (None, ES):
                remote_path = ES
                remote_display = f"{ES} (deduced)"
            else:
                remote_path = Path(item["path_cloud"]).as_posix()
                remote_display = remote_path
            remote_spec = f"{cloud}:{remote_path}"
            console.print(Panel(
                f"📦 PROCESSING: {display_name}\n"
                f"📂 Local path: {local_path}\n"
                f"☁️  Remote path: {remote_display}\n"
                f"🏳️  Flags: {flags or 'None'}",
                title=f"[bold blue]Processing Item: {display_name}[/bold blue]",
                border_style="blue",
            ))
            flag_arg = f" -{flags}" if flags else ""
            if direction == "BACKUP":
                program += f"""\ncloud copy "{local_path}" "{remote_spec}"{flag_arg}\n"""
            elif direction == "RETRIEVE":
                program += f"""\ncloud copy "{remote_spec}" "{local_path}"{flag_arg}\n"""
            else:
                console.print(Panel('❌ ERROR: INVALID DIRECTION\n⚠️  Direction must be either "BACKUP" or "RETRIEVE"', title="[bold red]Error: Invalid Direction[/bold red]", border_style="red"))
                raise RuntimeError(f"Unknown direction: {direction}")
            if group_name == "dotfiles" and system_raw == "Linux":
                program += """\nchmod 700 ~/.ssh/*\n"""
                console.print(Panel("🔒 SPECIAL HANDLING: SSH PERMISSIONS\n🛠️  Setting secure permissions for SSH files\n📝 Command: chmod 700 ~/.ssh/*", title="[bold blue]Special Handling: SSH Permissions[/bold blue]", border_style="blue"))
    print_code(program, lexer="shell", desc=f"{direction} script")
    console.print(Panel(f"✅ {direction} SCRIPT GENERATION COMPLETE\n🚀 Ready to execute the operations", title="[bold green]Script Generation Complete[/bold green]", border_style="green"))
    import subprocess

    subprocess.run(program, shell=True, check=True)


if __name__ == "__main__":
    pass
