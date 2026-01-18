import json
import re

from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.commands import ensure_ok, run_powershell
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.device_entry import DeviceEntry
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.utils import as_str, format_size_bytes


def _normalize_ps_json(raw_text: str) -> list[dict[str, object]]:
	if raw_text.strip() == "":
		return []
	data = json.loads(raw_text)
	if isinstance(data, list):
		return [x for x in data if isinstance(x, dict)]
	if isinstance(data, dict):
		return [data]
	return []


def list_windows_devices() -> list[DeviceEntry]:
	partitions_result = run_powershell(
		"Get-Partition | Select-Object DiskNumber,PartitionNumber,DriveLetter,Size,Type,Guid | ConvertTo-Json"
	)
	volumes_result = run_powershell(
		"Get-Volume | Select-Object DriveLetter,FileSystemLabel,FileSystem,Size,SizeRemaining,DriveType,Path | ConvertTo-Json"
	)
	partitions_text = ensure_ok(partitions_result, "Get-Partition")
	volumes_text = ensure_ok(volumes_result, "Get-Volume")
	partitions = _normalize_ps_json(partitions_text)
	volumes = _normalize_ps_json(volumes_text)
	volume_map: dict[str, dict[str, object]] = {}
	for volume in volumes:
		drive_letter = as_str(volume.get("DriveLetter"))
		if isinstance(drive_letter, str):
			volume_map[drive_letter.upper()] = volume
	entries: list[DeviceEntry] = []
	for partition in partitions:
		disk_number = partition.get("DiskNumber")
		partition_number = partition.get("PartitionNumber")
		drive_letter = as_str(partition.get("DriveLetter"))
		volume = volume_map.get(drive_letter.upper()) if isinstance(drive_letter, str) else None
		label = None
		fs_type = None
		mount_point = None
		extra = as_str(partition.get("Type"))
		if isinstance(volume, dict):
			label = as_str(volume.get("FileSystemLabel"))
			fs_type = as_str(volume.get("FileSystem"))
			mount_point = as_str(volume.get("Path"))
			if mount_point is None and isinstance(drive_letter, str) and drive_letter != "":
				mount_point = f"{drive_letter}:\\"
		size_value = partition.get("Size")
		size = format_size_bytes(size_value) if isinstance(size_value, int) else None
		key = f"Disk {disk_number} Part {partition_number}"
		device_path = as_str(partition.get("Guid")) or key
		entries.append(
			DeviceEntry(
				platform_name="Windows",
				key=key,
				device_path=device_path,
				device_type="part",
				label=label,
				mount_point=mount_point,
				fs_type=fs_type,
				size=size,
				extra=extra,
				disk_number=disk_number if isinstance(disk_number, int) else None,
				partition_number=partition_number if isinstance(partition_number, int) else None,
				drive_letter=drive_letter.upper() if isinstance(drive_letter, str) and drive_letter != "" else None,
			)
		)
	return entries


def _normalize_drive_letter(value: str) -> str:
	match = re.search(r"([A-Za-z])", value)
	if match is None:
		raise RuntimeError("Invalid drive letter")
	return match.group(1).upper()


def mount_windows(entry: DeviceEntry, mount_point: str) -> None:
	if entry.disk_number is None or entry.partition_number is None:
		raise RuntimeError("Partition details not available")
	letter = _normalize_drive_letter(mount_point)
	command = (
		f"Get-Partition -DiskNumber {entry.disk_number} -PartitionNumber {entry.partition_number} | "
		f"Set-Partition -NewDriveLetter {letter}"
	)
	result = run_powershell(command)
	ensure_ok(result, "Set-Partition")
