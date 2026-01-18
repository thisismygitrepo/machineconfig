import platform

from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.device_entry import DeviceEntry
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.linux import list_linux_devices
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.macos import list_macos_devices
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.windows import list_windows_devices


def list_devices() -> list[DeviceEntry]:
	platform_name = platform.system()
	if platform_name == "Linux":
		return list_linux_devices()
	if platform_name == "Darwin":
		return list_macos_devices()
	if platform_name == "Windows":
		return list_windows_devices()
	return []
