from machineconfig.utils.accessories import split_list
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig

from typing import Literal


def split_tabs_by_weight(tabs: list[TabConfig], max_weight: int) -> list[list[TabConfig]]:
    """Split tabs into chunks where each chunk's total weight <= max_weight."""
    chunks: list[list[TabConfig]] = []
    current_chunk: list[TabConfig] = []
    current_weight = 0
    for tab in tabs:
        tab_weight = tab.get("tabWeight", 1)
        if current_weight + tab_weight > max_weight and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [tab]
            current_weight = tab_weight
        else:
            current_chunk.append(tab)
            current_weight += tab_weight
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def combine_tabs_into_super_tabs(tabs: list[TabConfig], num_super_tabs: int) -> list[TabConfig]:
    """Combine tabs into num_super_tabs super tabs with combined commands."""
    if len(tabs) <= num_super_tabs:
        return tabs  # No need to combine
    
    tab_groups = split_list(tabs, to=num_super_tabs)
    super_tabs: list[TabConfig] = []
    for idx, group in enumerate(tab_groups):
        if len(group) == 1:
            super_tabs.append(group[0])
        else:
            combined_command = "; ".join(tab["command"] for tab in group)
            combined_name = f"super_tab_{idx+1}"
            # Use startDir of the first tab
            start_dir = group[0]["startDir"]
            # Sum weights
            total_weight = sum(tab.get("tabWeight", 1) for tab in group)
            super_tabs.append({
                "tabName": combined_name,
                "startDir": start_dir,
                "command": combined_command,
                "tabWeight": total_weight
            })
    return super_tabs


def combine_tabs_by_weight_into_super_tabs(tabs: list[TabConfig], max_weight: int) -> list[TabConfig]:
    """Combine tabs into super tabs where each super tab has weight <= max_weight."""
    tab_groups = split_tabs_by_weight(tabs, max_weight=max_weight)
    super_tabs: list[TabConfig] = []
    for idx, group in enumerate(tab_groups):
        if len(group) == 1:
            super_tabs.append(group[0])
        else:
            combined_command = "; ".join(tab["command"] for tab in group)
            combined_name = f"super_tab_{idx+1}"
            start_dir = group[0]["startDir"]
            total_weight = sum(tab.get("tabWeight", 1) for tab in group)
            super_tabs.append({
                "tabName": combined_name,
                "startDir": start_dir,
                "command": combined_command,
                "tabWeight": total_weight
            })
    return super_tabs


def restrict_num_tabs_helper1(layout_configs: list[LayoutConfig], max_thresh: int, threshold_type: Literal["number"], breaking_method: Literal["moreLayouts"]) -> list[LayoutConfig]:
    """When threshold is exceeded, create more layouts with max_thresh tabs each."""
    new_layout_configs: list[LayoutConfig] = []
    for a_layout_config in layout_configs:
        if len(a_layout_config["layoutTabs"]) > max_thresh:
            print(f"Layout '{a_layout_config['layoutName']}' has too many tabs ({len(a_layout_config['layoutTabs'])} > {max_thresh}). Splitting into multiple layouts.")
            tab_chunks = split_list(a_layout_config["layoutTabs"], every=max_thresh)
            for idx, tab_chunk in enumerate(tab_chunks):
                new_layout_configs.append({
                    "layoutName": f"{a_layout_config['layoutName']}_part{idx+1}",
                    "layoutTabs": tab_chunk
                })
        else:
            print(f"Layout '{a_layout_config['layoutName']}' has acceptable number of tabs ({len(a_layout_config['layoutTabs'])} <= {max_thresh}). Keeping as is.")
            new_layout_configs.append(a_layout_config)
    return new_layout_configs


def restrict_num_tabs_helper2(layout_configs: list[LayoutConfig], max_thresh: int, threshold_type: Literal["number"], breaking_method: Literal["combineTabs"]) -> list[LayoutConfig]:
    """When threshold is exceeded, combine tabs into super tabs to reduce count to max_thresh."""
    new_layout_configs: list[LayoutConfig] = []
    for a_layout_config in layout_configs:
        num_tabs = len(a_layout_config["layoutTabs"])
        if num_tabs > max_thresh:
            print(f"Layout '{a_layout_config['layoutName']}' has too many tabs ({num_tabs} > {max_thresh}). Combining into {max_thresh} super tabs.")
            super_tabs = combine_tabs_into_super_tabs(a_layout_config["layoutTabs"], num_super_tabs=max_thresh)
            new_layout_configs.append({
                "layoutName": a_layout_config["layoutName"],
                "layoutTabs": super_tabs
            })
        else:
            print(f"Layout '{a_layout_config['layoutName']}' has acceptable number of tabs ({num_tabs} <= {max_thresh}). Keeping as is.")
            new_layout_configs.append(a_layout_config)
    return new_layout_configs


def restrict_num_tabs_helper3(layout_configs: list[LayoutConfig], max_thresh: int, threshold_type: Literal["weight"], breaking_method: Literal["moreLayouts"]) -> list[LayoutConfig]:
    """When threshold is exceeded, create more layouts with max_thresh total weight each."""
    new_layout_configs: list[LayoutConfig] = []
    for a_layout_config in layout_configs:
        layout_weight = sum(tab.get("tabWeight", 1) for tab in a_layout_config["layoutTabs"])
        if layout_weight > max_thresh:
            print(f"Layout '{a_layout_config['layoutName']}' has too much weight ({layout_weight} > {max_thresh}). Splitting into multiple layouts.")
            tab_chunks = split_tabs_by_weight(a_layout_config["layoutTabs"], max_weight=max_thresh)
            for idx, tab_chunk in enumerate(tab_chunks):
                new_layout_configs.append({
                    "layoutName": f"{a_layout_config['layoutName']}_part{idx+1}",
                    "layoutTabs": tab_chunk
                })
        else:
            print(f"Layout '{a_layout_config['layoutName']}' has acceptable total weight ({layout_weight} <= {max_thresh}). Keeping as is.")
            new_layout_configs.append(a_layout_config)
    return new_layout_configs


def restrict_num_tabs_helper4(layout_configs: list[LayoutConfig], max_thresh: int, threshold_type: Literal["weight"], breaking_method: Literal["combineTabs"]) -> list[LayoutConfig]:
    """When threshold is exceeded, combine tabs into super tabs with weight <= max_thresh."""
    new_layout_configs: list[LayoutConfig] = []
    for a_layout_config in layout_configs:
        layout_weight = sum(tab.get("tabWeight", 1) for tab in a_layout_config["layoutTabs"])
        if layout_weight > max_thresh:
            print(f"Layout '{a_layout_config['layoutName']}' has too much weight ({layout_weight} > {max_thresh}). Combining into super tabs with weight <= {max_thresh}.")
            super_tabs = combine_tabs_by_weight_into_super_tabs(a_layout_config["layoutTabs"], max_weight=max_thresh)
            new_layout_configs.append({
                "layoutName": a_layout_config["layoutName"],
                "layoutTabs": super_tabs
            })
        else:
            print(f"Layout '{a_layout_config['layoutName']}' has acceptable total weight ({layout_weight} <= {max_thresh}). Keeping as is.")
            new_layout_configs.append(a_layout_config)
    return new_layout_configs
