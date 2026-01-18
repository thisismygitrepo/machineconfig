from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.device_entry import DeviceEntry
from machineconfig.scripts.python.helpers.helpers_devops.mount_helpers.utils import format_device


def pick_device(entries: list[DeviceEntry], header: str) -> DeviceEntry:
	from machineconfig.utils.options import choose_from_options

	options: list[str] = []
	map_option: dict[str, DeviceEntry] = {}
	for idx, entry in enumerate(entries):
		option = f"{idx:02d} {format_device(entry)}"
		options.append(option)
		map_option[option] = entry
	choice = choose_from_options(options=options, msg="Select a device", multi=False, header=header, tv=True)
	selected = map_option.get(choice)
	if selected is None:
		raise RuntimeError("Selection not found")
	return selected


def resolve_device(entries: list[DeviceEntry], query: str) -> DeviceEntry:
	query_value = query.strip()
	if query_value in {"?", ""}:
		return pick_device(entries, header="Available devices")
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
		return pick_device(exact_matches, header="Multiple matches")
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
		return pick_device(partial_matches, header="Multiple matches")
	return pick_device(entries, header="Available devices")
