
import json
import platform
import plistlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer



@dataclass(frozen=True)
class DeviceEntry:
	platform_name: str
	key: str
	device_path: str
	label: str | None
	mount_point: str | None
	fs_type: str | None
	size: str | None
	extra: str | None
	disk_number: int | None
	partition_number: int | None
	drive_letter: str | None


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
	result = subprocess.run(command, capture_output=True, text=True, check=False)
	return result


def _run_powershell(command: str) -> subprocess.CompletedProcess[str]:
	result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, check=False)
	return result


def _ensure_ok(result: subprocess.CompletedProcess[str], context: str) -> str:
	if result.returncode != 0:
		stderr_value = result.stderr.strip()
		stdout_value = result.stdout.strip()
		error_text = stderr_value if stderr_value != "" else stdout_value
		raise RuntimeError(f"{context} failed: {error_text}")
	return result.stdout


def _as_str(value: object) -> str | None:
	if isinstance(value, str) and value != "":
		return value
	return None


def _format_size_bytes(size_bytes: int) -> str:
	units = ["B", "KB", "MB", "GB", "TB", "PB"]
	value = float(size_bytes)
	unit_index = 0
	while value >= 1024 and unit_index < len(units) - 1:
		value = value / 1024
		unit_index += 1
	if unit_index == 0:
		return f"{int(value)} {units[unit_index]}"
	return f"{value:.1f} {units[unit_index]}"


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


def _list_linux_devices() -> list[DeviceEntry]:
	result = _run_command(["lsblk", "-J", "-o", "NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINT,UUID,MODEL"])
	text = _ensure_ok(result, "lsblk")
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
			label = _as_str(item.get("label"))
			mount_point = _as_str(item.get("mountpoint"))
			fs_type = _as_str(item.get("fstype"))
			size = _as_str(item.get("size"))
			model = _as_str(item.get("model"))
			entries.append(
				DeviceEntry(
					platform_name="Linux",
					key=name_value,
					device_path=device_path,
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


def _diskutil_info(identifier: str) -> dict[str, object]:
	result = _run_command(["diskutil", "info", "-plist", identifier])
	text = _ensure_ok(result, "diskutil info")
	return plistlib.loads(text.encode("utf-8"))


def _list_macos_devices() -> list[DeviceEntry]:
	result = _run_command(["diskutil", "list", "-plist"])
	text = _ensure_ok(result, "diskutil list")
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
					mount_point = _as_str(info.get("MountPoint"))
					label = _as_str(info.get("VolumeName"))
					fs_type = _as_str(info.get("FilesystemType"))
					if fs_type is None:
						fs_type = _as_str(info.get("FileSystemType"))
					size_value = info.get("TotalSize")
					size = _format_size_bytes(size_value) if isinstance(size_value, int) else None
					media_name = _as_str(info.get("MediaName"))
					device_path = f"/dev/{identifier}"
					entries.append(
						DeviceEntry(
							platform_name="Darwin",
							key=identifier,
							device_path=device_path,
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
				mount_point = _as_str(info.get("MountPoint"))
				label = _as_str(info.get("VolumeName"))
				fs_type = _as_str(info.get("FilesystemType"))
				if fs_type is None:
					fs_type = _as_str(info.get("FileSystemType"))
				size_value = info.get("TotalSize")
				size = _format_size_bytes(size_value) if isinstance(size_value, int) else None
				media_name = _as_str(info.get("MediaName"))
				device_path = f"/dev/{identifier}"
				entries.append(
					DeviceEntry(
						platform_name="Darwin",
						key=identifier,
						device_path=device_path,
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


def _normalize_ps_json(raw_text: str) -> list[dict[str, object]]:
	if raw_text.strip() == "":
		return []
	data = json.loads(raw_text)
	if isinstance(data, list):
		return [x for x in data if isinstance(x, dict)]
	if isinstance(data, dict):
		return [data]
	return []


def _list_windows_devices() -> list[DeviceEntry]:
	partitions_result = _run_powershell(
		"Get-Partition | Select-Object DiskNumber,PartitionNumber,DriveLetter,Size,Type,Guid | ConvertTo-Json"
	)
	volumes_result = _run_powershell(
		"Get-Volume | Select-Object DriveLetter,FileSystemLabel,FileSystem,Size,SizeRemaining,DriveType,Path | ConvertTo-Json"
	)
	partitions_text = _ensure_ok(partitions_result, "Get-Partition")
	volumes_text = _ensure_ok(volumes_result, "Get-Volume")
	partitions = _normalize_ps_json(partitions_text)
	volumes = _normalize_ps_json(volumes_text)
	volume_map: dict[str, dict[str, object]] = {}
	for volume in volumes:
		drive_letter = _as_str(volume.get("DriveLetter"))
		if isinstance(drive_letter, str):
			volume_map[drive_letter.upper()] = volume
	entries: list[DeviceEntry] = []
	for partition in partitions:
		disk_number = partition.get("DiskNumber")
		partition_number = partition.get("PartitionNumber")
		drive_letter = _as_str(partition.get("DriveLetter"))
		volume = volume_map.get(drive_letter.upper()) if isinstance(drive_letter, str) else None
		label = None
		fs_type = None
		mount_point = None
		extra = _as_str(partition.get("Type"))
		if isinstance(volume, dict):
			label = _as_str(volume.get("FileSystemLabel"))
			fs_type = _as_str(volume.get("FileSystem"))
			mount_point = _as_str(volume.get("Path"))
			if mount_point is None and isinstance(drive_letter, str) and drive_letter != "":
				mount_point = f"{drive_letter}:\\"
		size_value = partition.get("Size")
		size = _format_size_bytes(size_value) if isinstance(size_value, int) else None
		key = f"Disk {disk_number} Part {partition_number}"
		device_path = _as_str(partition.get("Guid")) or key
		entries.append(
			DeviceEntry(
				platform_name="Windows",
				key=key,
				device_path=device_path,
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


def _list_devices() -> list[DeviceEntry]:
	platform_name = platform.system()
	if platform_name == "Linux":
		return _list_linux_devices()
	if platform_name == "Darwin":
		return _list_macos_devices()
	if platform_name == "Windows":
		return _list_windows_devices()
	return []


def _format_device(entry: DeviceEntry) -> str:
	label = entry.label if entry.label is not None and entry.label != "" else "-"
	fs_type = entry.fs_type if entry.fs_type is not None and entry.fs_type != "" else "-"
	size = entry.size if entry.size is not None and entry.size != "" else "-"
	mount_point = entry.mount_point if entry.mount_point is not None and entry.mount_point != "" else "-"
	extra = entry.extra if entry.extra is not None and entry.extra != "" else "-"
	return f"{entry.key} | {entry.device_path} | {fs_type} | {size} | {mount_point} | {label} | {extra}"


def _pick_device(entries: list[DeviceEntry], header: str) -> DeviceEntry:
	from machineconfig.utils.options import choose_from_options
	options: list[str] = []
	map_option: dict[str, DeviceEntry] = {}
	for idx, entry in enumerate(entries):
		option = f"{idx:02d} { _format_device(entry)}"
		options.append(option)
		map_option[option] = entry
	choice = choose_from_options(options=options, msg="Select a device", multi=False, header=header, tv=True)
	selected = map_option.get(choice)
	if selected is None:
		raise RuntimeError("Selection not found")
	return selected


def _resolve_device(entries: list[DeviceEntry], query: str) -> DeviceEntry:
	query_value = query.strip()
	if query_value in {"?", ""}:
		return _pick_device(entries, header="Available devices")
	exact_matches = [
		entry
		for entry in entries
		if entry.device_path.lower() == query_value.lower()
		or entry.key.lower() == query_value.lower()
		or (entry.label is not None and entry.label.lower() == query_value.lower())
	]
	if len(exact_matches) == 1:
		return exact_matches[0]
	if len(exact_matches) > 1:
		return _pick_device(exact_matches, header="Multiple matches")
	partial_matches = [
		entry
		for entry in entries
		if query_value.lower() in entry.device_path.lower()
		or query_value.lower() in entry.key.lower()
		or (entry.label is not None and query_value.lower() in entry.label.lower())
	]
	if len(partial_matches) == 1:
		return partial_matches[0]
	if len(partial_matches) > 1:
		return _pick_device(partial_matches, header="Multiple matches")
	return _pick_device(entries, header="Available devices")


def _mount_linux(entry: DeviceEntry, mount_point: str) -> None:
	mount_path = Path(mount_point)
	mount_path.mkdir(parents=True, exist_ok=True)
	result = _run_command(["mount", entry.device_path, str(mount_path)])
	_ensure_ok(result, "mount")


def _mount_macos(entry: DeviceEntry, mount_point: str) -> None:
	if mount_point == "-":
		result = _run_command(["diskutil", "mount", entry.key])
		_ensure_ok(result, "diskutil mount")
		return
	mount_path = Path(mount_point)
	mount_path.mkdir(parents=True, exist_ok=True)
	result = _run_command(["diskutil", "mount", "-mountPoint", str(mount_path), entry.key])
	_ensure_ok(result, "diskutil mount")


def _normalize_drive_letter(value: str) -> str:
	match = re.search(r"([A-Za-z])", value)
	if match is None:
		raise RuntimeError("Invalid drive letter")
	return match.group(1).upper()


def _mount_windows(entry: DeviceEntry, mount_point: str) -> None:
	if entry.disk_number is None or entry.partition_number is None:
		raise RuntimeError("Partition details not available")
	letter = _normalize_drive_letter(mount_point)
	command = f"Get-Partition -DiskNumber {entry.disk_number} -PartitionNumber {entry.partition_number} | Set-Partition -NewDriveLetter {letter}"
	result = _run_powershell(command)
	_ensure_ok(result, "Set-Partition")


def list_devices() -> None:
	entries = _list_devices()
	if not entries:
		typer.echo("No devices found")
		return
	for entry in entries:
		typer.echo(_format_device(entry))


def mount_device(
	device_query: Annotated[str, typer.Argument(...)],
	mount_point: Annotated[str, typer.Argument(...)],
) -> None:
	try:
		entries = _list_devices()
		if not entries:
			typer.echo("No devices found")
			raise typer.Exit(1)
		entry = _resolve_device(entries, device_query)
		platform_name = platform.system()
		if platform_name == "Linux":
			_mount_linux(entry, mount_point)
		elif platform_name == "Darwin":
			_mount_macos(entry, mount_point)
		elif platform_name == "Windows":
			_mount_windows(entry, mount_point)
		else:
			typer.echo(f"Unsupported platform: {platform_name}")
			raise typer.Exit(1)
		typer.echo("Mount completed")
	except RuntimeError as exc:
		typer.echo(f"Mount failed: {exc}")
		raise typer.Exit(1)


def mount_interactive() -> None:
	try:
		entries = _list_devices()
		if not entries:
			typer.echo("No devices found")
			raise typer.Exit(1)
		entry = _pick_device(entries, header="Available devices")
		platform_name = platform.system()
		if platform_name == "Darwin":
			mount_point = typer.prompt("Mount point (use '-' for default)")
		else:
			mount_point = typer.prompt("Mount point")
		if platform_name == "Linux":
			_mount_linux(entry, mount_point)
		elif platform_name == "Darwin":
			_mount_macos(entry, mount_point)
		elif platform_name == "Windows":
			_mount_windows(entry, mount_point)
		else:
			typer.echo(f"Unsupported platform: {platform_name}")
			raise typer.Exit(1)
		typer.echo("Mount completed")
	except RuntimeError as exc:
		typer.echo(f"Mount failed: {exc}")
		raise typer.Exit(1)

