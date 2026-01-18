import plistlib
from pathlib import Path

from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.commands import ensure_ok, run_command
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.device_entry import DeviceEntry
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.utils import as_str, format_size_bytes


def _diskutil_info(identifier: str) -> dict[str, object]:
	result = run_command(["diskutil", "info", "-plist", identifier])
	text = ensure_ok(result, "diskutil info")
	return plistlib.loads(text.encode("utf-8"))


def list_macos_devices() -> list[DeviceEntry]:
	result = run_command(["diskutil", "list", "-plist"])
	text = ensure_ok(result, "diskutil list")
	data = plistlib.loads(text.encode("utf-8"))
	entries: list[DeviceEntry] = []
	all_disks = data.get("AllDisksAndPartitions")
	if isinstance(all_disks, list):
		for disk in all_disks:
			if not isinstance(disk, dict):
				continue
			partitions = disk.get("Partitions")
			if isinstance(partitions, list) and partitions:
				for partition in partitions:
					if not isinstance(partition, dict):
						continue
					identifier = partition.get("DeviceIdentifier")
					if not isinstance(identifier, str):
						continue
					info = _diskutil_info(identifier)
					mount_point = as_str(info.get("MountPoint"))
					label = as_str(info.get("VolumeName"))
					fs_type = as_str(info.get("FilesystemType"))
					if fs_type is None:
						fs_type = as_str(info.get("FileSystemType"))
					size_value = info.get("TotalSize")
					size = format_size_bytes(size_value) if isinstance(size_value, int) else None
					media_name = as_str(info.get("MediaName"))
					device_path = f"/dev/{identifier}"
					entries.append(
						DeviceEntry(
							platform_name="Darwin",
							key=identifier,
							device_path=device_path,
							device_type="part",
							label=label,
							mount_point=mount_point,
							fs_type=fs_type,
							size=size,
							extra=media_name,
							disk_number=None,
							partition_number=None,
							drive_letter=None,
						)
					)
			else:
				identifier = disk.get("DeviceIdentifier")
				if not isinstance(identifier, str):
					continue
				info = _diskutil_info(identifier)
				mount_point = as_str(info.get("MountPoint"))
				label = as_str(info.get("VolumeName"))
				fs_type = as_str(info.get("FilesystemType"))
				if fs_type is None:
					fs_type = as_str(info.get("FileSystemType"))
				size_value = info.get("TotalSize")
				size = format_size_bytes(size_value) if isinstance(size_value, int) else None
				media_name = as_str(info.get("MediaName"))
				device_path = f"/dev/{identifier}"
				entries.append(
					DeviceEntry(
						platform_name="Darwin",
						key=identifier,
						device_path=device_path,
						device_type="disk",
						label=label,
						mount_point=mount_point,
						fs_type=fs_type,
						size=size,
						extra=media_name,
						disk_number=None,
						partition_number=None,
						drive_letter=None,
					)
				)
	return entries


def mount_macos(entry: DeviceEntry, mount_point: str) -> None:
	if mount_point == "-":
		result = run_command(["diskutil", "mount", entry.key])
		ensure_ok(result, "diskutil mount")
		return
	mount_path = Path(mount_point)
	mount_path.mkdir(parents=True, exist_ok=True)
	result = run_command(["diskutil", "mount", "-mountPoint", str(mount_path), entry.key])
	ensure_ok(result, "diskutil mount")
