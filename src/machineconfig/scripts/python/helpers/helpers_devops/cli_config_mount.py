
import platform
from typing import Annotated

import typer

from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.devices import list_devices as list_devices_internal
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.linux import mount_linux, select_linux_partition
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.macos import mount_macos
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.selection import pick_device, resolve_device
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.utils import format_device
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.windows import mount_windows


def list_devices() -> None:
	entries = list_devices_internal()
	if not entries:
		typer.echo("No devices found")
		return
	for entry in entries:
		typer.echo(format_device(entry))


def mount_device(
	device_query: Annotated[str, typer.Argument(...)],
	mount_point: Annotated[str, typer.Argument(...)],
) -> None:
	try:
		entries = list_devices_internal()
		if not entries:
			typer.echo("No devices found")
			raise typer.Exit(1)
		entry = resolve_device(entries, device_query)
		platform_name = platform.system()
		if platform_name == "Linux":
			selected = select_linux_partition(entries, entry)
			mount_linux(selected, mount_point)
		elif platform_name == "Darwin":
			mount_macos(entry, mount_point)
		elif platform_name == "Windows":
			mount_windows(entry, mount_point)
		else:
			typer.echo(f"Unsupported platform: {platform_name}")
			raise typer.Exit(1)
		typer.echo("Mount completed")
	except RuntimeError as exc:
		typer.echo(f"Mount failed: {exc}")
		raise typer.Exit(1)


def mount_interactive() -> None:
	try:
		entries = list_devices_internal()
		if not entries:
			typer.echo("No devices found")
			raise typer.Exit(1)
		entry = pick_device(entries, header="Available devices")
		platform_name = platform.system()
		if platform_name == "Darwin":
			mount_point = typer.prompt("Mount point (use '-' for default)")
		else:
			mount_point = typer.prompt("Mount point")
		if platform_name == "Linux":
			selected = select_linux_partition(entries, entry)
			mount_linux(selected, mount_point)
		elif platform_name == "Darwin":
			mount_macos(entry, mount_point)
		elif platform_name == "Windows":
			mount_windows(entry, mount_point)
		else:
			typer.echo(f"Unsupported platform: {platform_name}")
			raise typer.Exit(1)
		typer.echo("Mount completed")
	except RuntimeError as exc:
		typer.echo(f"Mount failed: {exc}")
		raise typer.Exit(1)

