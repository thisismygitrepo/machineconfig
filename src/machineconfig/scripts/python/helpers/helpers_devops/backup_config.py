"""Backup configuration types, parsing, and reading utilities."""

from collections.abc import Mapping
from typing import TypedDict
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import tomllib

from machineconfig.utils.source_of_truth import LIBRARY_ROOT
from machineconfig.profile.create_links_export import REPO_LOOSE

LIBRARY_BACKUP_PATH = LIBRARY_ROOT.joinpath("profile/mapper_data.toml")
USER_BACKUP_PATH = Path.home().joinpath("dotfiles/machineconfig/mapper_data.toml")
DEFAULT_BACKUP_HEADER = "# User-defined backup configuration\n# Created by `devops data register`\n"
VALID_OS = {"any", "windows", "linux", "darwin"}


class BackupItem(TypedDict):
    path_local: str
    path_cloud: str | None
    zip: bool
    encrypt: bool
    rel2home: bool
    os: set[str]


BackupGroup = dict[str, BackupItem]
BackupConfig = dict[str, BackupGroup]


def normalize_os_name(value: str) -> str:
    return value.strip().lower()


def _parse_os_field(os_field: object, item_name: str) -> set[str]:
    if os_field is None:
        raise ValueError(f"Backup entry '{item_name}' must define a non-empty 'os'.")
    if isinstance(os_field, list):
        raw_values = [str(item) for item in os_field]
    elif isinstance(os_field, str):
        raw_values = os_field.split(",")
    else:
        raise ValueError(f"Backup entry '{item_name}' has an invalid 'os' value: {os_field!r}.")
    values: set[str] = set()
    for raw in raw_values:
        token = normalize_os_name(raw)
        if not token:
            continue
        if token in {"any", "all", "*"}:
            return {"any"}
        if token not in VALID_OS:
            raise ValueError(f"Backup entry '{item_name}' has an invalid 'os' value: {os_field!r}.")
        values.add(token)
    if not values:
        raise ValueError(f"Backup entry '{item_name}' must define a non-empty 'os'.")
    return values


def os_applies(os_values: set[str], system_name: str) -> bool:
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
    for group_name, group_value in raw.items():
        group = _require_mapping(group_value, group_name)
        group_items: dict[str, BackupItem] = {}
        for item_name, value in group.items():
            item_key = f"{group_name}.{item_name}"
            item = _require_mapping(value, item_key)
            if "path" in item:
                raise ValueError(f"Backup entry '{item_key}' uses 'path'; use 'path_local' instead.")
            if "path_remote" in item:
                raise ValueError(f"Backup entry '{item_key}' uses 'path_remote'; use 'path_cloud' instead.")
            if "os_specific" in item:
                raise ValueError(f"Backup entry '{item_key}' uses 'os_specific'; use 'os' only.")
            group_items[item_name] = {
                "path_local": _require_str_field(item, "path_local", item_key),
                "path_cloud": _optional_str_field(item, "path_cloud", item_key),
                "zip": _require_bool_field(item, "zip", item_key),
                "encrypt": _require_bool_field(item, "encrypt", item_key),
                "rel2home": _require_bool_field(item, "rel2home", item_key),
                "os": _parse_os_field(item.get("os"), item_key),
            }
        if group_items:
            config[group_name] = group_items
    return config


def read_backup_config(repo: REPO_LOOSE) -> BackupConfig:
    match repo:
        case "library" | "l":
            path = LIBRARY_BACKUP_PATH
            raw_config: dict[str, object] = tomllib.loads(path.read_text(encoding="utf-8"))
            bu_file = _parse_backup_config(raw_config)
        case "user" | "u":
            path = USER_BACKUP_PATH
            raw_config = tomllib.loads(path.read_text(encoding="utf-8"))
            bu_file = _parse_backup_config(raw_config)
        case "all" | "a":
            console = Console()
            console.print(Panel(f"🧰 LOADING LIBRARY BACKUP CONFIGURATION\n📄 File: {LIBRARY_BACKUP_PATH}", title="[bold blue]Backup Configuration[/bold blue]", border_style="blue"))
            raw_library: dict[str, object] = tomllib.loads(LIBRARY_BACKUP_PATH.read_text(encoding="utf-8"))
            bu_library = _parse_backup_config(raw_library)
            console.print(Panel(f"🧰 LOADING USER BACKUP CONFIGURATION\n📄 File: {USER_BACKUP_PATH}", title="[bold blue]Backup Configuration[/bold blue]", border_style="blue"))
            raw_user: dict[str, object] = tomllib.loads(USER_BACKUP_PATH.read_text(encoding="utf-8"))
            bu_user = _parse_backup_config(raw_user)
            bu_file = {**bu_library, **bu_user}
        case _:
            raise ValueError(f"Invalid which_backup value: {repo!r}.")
    return bu_file
