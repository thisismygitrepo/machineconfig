from typing import Any


def collect_status_data_from_managers(managers: list[Any]) -> list[dict[str, Any]]:
    statuses = []
    for manager in managers:
        tabs = manager.layout_config["layoutTabs"]
        if hasattr(manager, "process_monitor"):
            a_status = manager.process_monitor.check_all_commands_status(tabs)
        else:
            a_status = manager.check_all_commands_status()
        statuses.append(a_status)
    return statuses


def flatten_status_data(statuses: list[dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    keys = []
    values = []
    for item in statuses:
        keys.extend(item.keys())
        values.extend(item.values())
    
    status_data = []
    for i, key in enumerate(keys):
        if i < len(values):
            status_data.append({"tabName": key, "status": values[i]})
    return status_data


def check_if_all_stopped(status_data: list[dict[str, Any]]) -> bool:
    running_count = sum(1 for item in status_data if item.get("status", {}).get("running", False))
    return running_count == 0


def print_status_table(status_data: list[dict[str, Any]]) -> None:
    for item in status_data:
        print(f"Tab: {item['tabName']}, Status: {item['status']}")


def collect_session_statuses(managers: list[Any]) -> list[dict[str, Any]]:
    statuses = []
    for manager in managers:
        a_status = manager.session_manager.check_wt_session_status()
        statuses.append(a_status)
    return statuses


def print_session_statuses(statuses: list[dict[str, Any]]) -> None:
    for i, status in enumerate(statuses):
        print(f"Manager {i}: {status}")
