
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig
# from machineconfig.utils.accessories import split_list
from typing import Literal, Protocol
from machineconfig.cluster.sessions_managers.helpers.load_balancer_helper import restrict_num_tabs_helper1, restrict_num_tabs_helper2, restrict_num_tabs_helper3, restrict_num_tabs_helper4

class COMMAND_SPLITTER(Protocol):
    def __call__(self, command: str, to: int) -> list[str]: ...


def limit_tab_num(layout_configs: list[LayoutConfig], max_thresh: int, threshold_type: Literal["number", "weight"], breaking_method: Literal["moreLayouts", "combineTabs"]) -> list[LayoutConfig]:
    match threshold_type, breaking_method:
        case "number", "moreLayouts":
            return restrict_num_tabs_helper1(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
        case "number", "combineTabs":
            return restrict_num_tabs_helper2(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
        case "weight", "moreLayouts":
            return restrict_num_tabs_helper3(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
        case "weight", "combineTabs":
            return restrict_num_tabs_helper4(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
        case _:
            raise NotImplementedError(f"The combination {threshold_type}, {breaking_method} is not implemented")
def limit_tab_weight(layout_configs: list[LayoutConfig], max_weight: int, command_splitter: COMMAND_SPLITTER) -> list[LayoutConfig]:
    new_layout_configs: list[LayoutConfig] = []
    for a_layout_config in layout_configs:
        new_tabs: list[TabConfig] = []
        for tab in a_layout_config["layoutTabs"]:
            tab_weight = tab.get("tabWeight", 1)
            if tab_weight > max_weight:
                print(f"Tab '{tab['tabName']}' in layout '{a_layout_config['layoutName']}' has too much weight ({tab_weight} > {max_weight}). Splitting command.")
                split_commands = command_splitter(tab["command"], to=max_weight)
                for idx, cmd in enumerate(split_commands):
                    new_tabs.append({
                        "tabName": f"{tab['tabName']}_part{idx+1}",
                        "startDir": tab["startDir"],
                        "command": cmd,
                        "tabWeight": max_weight
                    })
            else:
                new_tabs.append(tab)
        new_layout_configs.append({
            "layoutName": a_layout_config["layoutName"],
            "layoutTabs": new_tabs
        })
    return new_layout_configs


def run(layouts: list[LayoutConfig]):
    from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
    manager = ZellijLocalManager(session_layouts=layouts)
    manager.start_all_sessions(poll_interval=2, poll_seconds=2)
    manager.run_monitoring_routine(wait_ms=2000)
    manager.kill_all_sessions()
