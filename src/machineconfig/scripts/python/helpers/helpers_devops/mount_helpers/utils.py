from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.device_entry import DeviceEntry


def as_str(value: object) -> str | None:
	if isinstance(value, str) and value != "":
		return value
	return None


def format_size_bytes(size_bytes: int) -> str:
	units = ["B", "KB", "MB", "GB", "TB", "PB"]
	value = float(size_bytes)
	unit_index = 0
	while value >= 1024 and unit_index < len(units) - 1:
		value = value / 1024
		unit_index += 1
	if unit_index == 0:
		return f"{int(value)} {units[unit_index]}"
	return f"{value:.1f} {units[unit_index]}"


def format_device(entry: DeviceEntry) -> str:
	label = entry.label if entry.label is not None and entry.label != "" else "-"
	fs_type = entry.fs_type if entry.fs_type is not None and entry.fs_type != "" else "-"
	size = entry.size if entry.size is not None and entry.size != "" else "-"
	mount_point = entry.mount_point if entry.mount_point is not None and entry.mount_point != "" else "-"
	extra = entry.extra if entry.extra is not None and entry.extra != "" else "-"
	return f"{entry.key} | {entry.device_path} | {fs_type} | {size} | {mount_point} | {label} | {extra}"
