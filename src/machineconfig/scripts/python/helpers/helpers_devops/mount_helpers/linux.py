import json
import os
from pathlib import Path

from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.commands import ensure_ok, run_command, run_command_sudo
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.device_entry import DeviceEntry
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.selection import pick_device
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.utils import as_str


def _flatten_lsblk_devices(devices: list[dict[str, object]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    stack = list(devices)
    while stack:
        item = stack.pop(0)
        result.append(item)
        children = item.get("children")
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    stack.append(child)
    return result


def list_linux_devices() -> list[DeviceEntry]:
    result = run_command(["lsblk", "-J", "-o", "NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINT,UUID,MODEL"])
    text = ensure_ok(result, "lsblk")
    data = json.loads(text)
    raw_devices = data.get("blockdevices")
    entries: list[DeviceEntry] = []
    if isinstance(raw_devices, list):
        for item in _flatten_lsblk_devices(raw_devices):
            name_value = item.get("name")
            if not isinstance(name_value, str):
                continue
            device_type = item.get("type")
            if not isinstance(device_type, str):
                continue
            if device_type not in {"disk", "part"}:
                continue
            device_path = f"/dev/{name_value}"
            label = as_str(item.get("label"))
            mount_point = as_str(item.get("mountpoint"))
            fs_type = as_str(item.get("fstype"))
            size = as_str(item.get("size"))
            model = as_str(item.get("model"))
            entries.append(
                DeviceEntry(
                    platform_name="Linux",
                    key=name_value,
                    device_path=device_path,
                    device_type=device_type,
                    label=label,
                    mount_point=mount_point,
                    fs_type=fs_type,
                    size=size,
                    extra=model,
                    disk_number=None,
                    partition_number=None,
                    drive_letter=None,
                )
            )
    return entries


def mount_linux(entry: DeviceEntry, mount_point: str) -> None:
    mount_path = Path(mount_point)
    try:
        mount_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        mkdir_result = run_command_sudo(["mkdir", "-p", str(mount_path)])
        ensure_ok(mkdir_result, "mkdir")
    if os.geteuid() == 0:
        result = run_command(["mount", entry.device_path, str(mount_path)])
    else:
        result = run_command_sudo(["mount", entry.device_path, str(mount_path)])
    ensure_ok(result, "mount")


def _is_partition_of_disk(partition: DeviceEntry, disk: DeviceEntry) -> bool:
    if partition.device_type != "part" or disk.device_type != "disk":
        return False
    if partition.key == disk.key:
        return False
    if not partition.key.startswith(disk.key):
        return False
    return True


def select_linux_partition(entries: list[DeviceEntry], entry: DeviceEntry) -> DeviceEntry:
    if entry.device_type != "disk":
        return entry
    candidates = [device for device in entries if _is_partition_of_disk(device, entry)]
    with_fs = [device for device in candidates if device.fs_type is not None and device.fs_type != ""]
    if len(with_fs) == 1:
        return with_fs[0]
    if len(with_fs) > 1:
        return pick_device(with_fs, header="Select partition to mount")
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        return pick_device(candidates, header="Select partition to mount")
    raise RuntimeError("No mountable partitions found for selected disk")
