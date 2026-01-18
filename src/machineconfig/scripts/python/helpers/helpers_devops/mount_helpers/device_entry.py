from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceEntry:
	platform_name: str
	key: str
	device_path: str
	device_type: str | None
	label: str | None
	mount_point: str | None
	fs_type: str | None
	size: str | None
	extra: str | None
	disk_number: int | None
	partition_number: int | None
	drive_letter: str | None
