#!/usr/bin/env python3
"""
Helper functions for generating Zellij KDL layouts with support for multiple panes per tab.
This module extends the basic layout functionality to organize multiple commands into panes within a single tab.
"""
import shlex
import random
import string
import logging
from pathlib import Path
from typing import Literal

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, TabConfig


logger = logging.getLogger(__name__)


def generate_random_suffix(length: int) -> str:
    """Generate a random string suffix for unique layout file names."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def parse_command(command: str) -> tuple[str, list[str]]:
    """Parse a command string into executable and arguments."""
    try:
        parts = shlex.split(command)
        if not parts:
            raise ValueError("Empty command provided")
        return parts[0], parts[1:] if len(parts) > 1 else []
    except ValueError as e:
        logger.error(f"Error parsing command '{command}': {e}")
        parts = command.split()
        return parts[0] if parts else "", parts[1:] if len(parts) > 1 else []


def format_args_for_kdl(args: list[str]) -> str:
    """Format command arguments for KDL layout format."""
    if not args:
        return ""
    formatted_args = []
    for arg in args:
        if " " in arg or '"' in arg or "'" in arg:
            escaped_arg = arg.replace('"', '\\"')
            formatted_args.append(f'"{escaped_arg}"')
        else:
            formatted_args.append(f'"{arg}"')
    return " ".join(formatted_args)


def create_pane_kdl(tab_config: TabConfig, indent_level: int) -> str:
    """Create a KDL pane definition from a tab configuration."""
    indent = "  " * indent_level
    cmd, args = parse_command(tab_config["command"])
    args_str = format_args_for_kdl(args)
    pane_content = f'{indent}pane command="{cmd}" {{\n'
    if args_str:
        pane_content += f'{indent}  args {args_str}\n'
    pane_content += f'{indent}}}\n'
    return pane_content


def create_tab_with_panes(
    tab_configs: list[TabConfig],
    tab_name: str,
    common_cwd: str,
    split_direction: Literal["vertical", "horizontal"] = "vertical",
) -> str:
    """
    Create a KDL tab section with multiple panes from multiple tab configurations.
    
    Args:
        tab_configs: List of TabConfig objects to be organized as panes within one tab
        tab_name: Name for the tab (derived from configs)
        common_cwd: Common working directory for the tab
        split_direction: Direction to split panes ('vertical' or 'horizontal')
    
    Returns:
        KDL formatted string for the tab with multiple panes
    """
    escaped_tab_name = tab_name.replace('"', '\\"')
    tab_section = f'  tab name="{escaped_tab_name}" cwd="{common_cwd}" {{\n'
    if len(tab_configs) == 1:
        cmd, args = parse_command(tab_configs[0]["command"])
        args_str = format_args_for_kdl(args)
        tab_section += f'    pane command="{cmd}" {{\n'
        if args_str:
            tab_section += f"      args {args_str}\n"
        tab_section += "    }\n"
    else:
        tab_section += f'    pane split_direction="{split_direction}" {{\n'
        for config in tab_configs:
            tab_section += create_pane_kdl(config, indent_level=3)
        tab_section += "    }\n"
    tab_section += "  }\n"
    return tab_section


def generate_tab_name(tab_configs: list[TabConfig], tab_index: int) -> str:
    """
    Generate a meaningful tab name from a list of tab configurations.
    
    Args:
        tab_configs: List of TabConfig objects in this tab
        tab_index: Index of the tab (1-based)
    
    Returns:
        A descriptive tab name
    """
    if len(tab_configs) == 1:
        return tab_configs[0]["tabName"]
    first_name = tab_configs[0]["tabName"].strip()
    if first_name.startswith("🤖") or first_name.startswith("📊") or first_name.startswith("📝"):
        base_name = first_name[:2]
        return f"{base_name}Group{tab_index}"
    words = first_name.split()
    if words:
        first_word = words[0].strip(":")
        return f"{first_word}×{len(tab_configs)}"
    return f"Tab{tab_index}[{len(tab_configs)}]"


def determine_common_cwd(tab_configs: list[TabConfig]) -> str:
    """
    Determine the common working directory for a group of tab configs.
    
    Args:
        tab_configs: List of TabConfig objects
    
    Returns:
        The most common directory or the first one if no commonality
    """
    if not tab_configs:
        return "~"
    dirs = [config["startDir"] for config in tab_configs]
    if len(set(dirs)) == 1:
        return dirs[0]
    return dirs[0]


def create_zellij_layout_with_panes(
    layout_config: LayoutConfig,
    output_path: str,
    panes_per_tab: int = 1,
    split_direction: Literal["vertical", "horizontal"] = "vertical",
) -> str:
    """
    Create a Zellij KDL layout file with support for multiple panes per tab.
    
    Args:
        layout_config: The LayoutConfig object containing all tabs/commands
        panes_per_tab: Number of panes to group into each tab (default: 1 = same as original behavior)
        split_direction: Direction to split panes within a tab ('vertical' or 'horizontal')
        output_path: Path to save the layout file (directory or full file path)
    
    Returns:
        Absolute path to the created layout file
    
    Example:
        >>> layout = {"layoutName": "MyLayout", "layoutTabs": [...]}
        >>> path = create_zellij_layout_with_panes(layout, panes_per_tab=2, split_direction="vertical", output_path="/tmp/layout.kdl")
    """
    if panes_per_tab < 1:
        raise ValueError("panes_per_tab must be at least 1")
    layout_tabs = layout_config["layoutTabs"]
    if not layout_tabs:
        raise ValueError("Layout must contain at least one tab")
    layout_template = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""
    layout_content = layout_template
    grouped_tabs: list[list[TabConfig]] = []
    for i in range(0, len(layout_tabs), panes_per_tab):
        group = layout_tabs[i : i + panes_per_tab]
        grouped_tabs.append(group)
    for tab_index, group in enumerate(grouped_tabs, start=1):
        tab_name = generate_tab_name(group, tab_index)
        common_cwd = determine_common_cwd(group)
        layout_content += "\n" + create_tab_with_panes(group, tab_name, common_cwd, split_direction)
    layout_content += "\n}\n"
    try:
        path_obj = Path(output_path)
        if path_obj.is_dir():
            raise ValueError("Output path must be a file path ending with .kdl, not a directory")
        if path_obj.suffix == ".kdl":
            layout_file = path_obj
            layout_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise ValueError("Output path must end with .kdl")
        layout_file.write_text(layout_content, encoding="utf-8")
        logger.info(f"Created Zellij layout file: {layout_file.absolute()}")
        return str(layout_file.absolute())
    except OSError as e:
        logger.error(f"Failed to create layout file: {e}")
        raise


if __name__ == "__main__":
    sample_layout: LayoutConfig = {
        "layoutName": "TestMultiPane",
        "layoutTabs": [
            {"tabName": "🤖Bot1", "startDir": "~/code/project1", "command": "python bot1.py"},
            {"tabName": "🤖Bot2", "startDir": "~/code/project1", "command": "python bot2.py"},
            {"tabName": "🤖Bot3", "startDir": "~/code/project1", "command": "python bot3.py"},
            {"tabName": "🤖Bot4", "startDir": "~/code/project2", "command": "python bot4.py"},
            {"tabName": "📊Monitor", "startDir": "~", "command": "htop"},
            {"tabName": "📝Logs", "startDir": "/var/log", "command": "tail -f /var/log/app.log"},
        ],
    }
    print("=" * 80)
    print("DEMO 1: panes_per_tab=1 (same as original behavior)")
    print("=" * 80)
    layout_path_1 = create_zellij_layout_with_panes(sample_layout, "/tmp/zellij_test_123.kdl", panes_per_tab=1)
    print(f"✅ Layout created: {layout_path_1}")
    layout_path_2 = create_zellij_layout_with_panes(layout_config=sample_layout, output_path="/tmp/zellij_test_1234.kdl", panes_per_tab=2, split_direction="vertical")
    print(f"✅ Layout created: {layout_path_2}")
    print("DEMO 3: panes_per_tab=3 (three panes per tab, horizontal split)")
    layout_path_3 = create_zellij_layout_with_panes(layout_config=sample_layout, output_path="/tmp/zellij_test_12345.kdl", panes_per_tab=3, split_direction="horizontal")
    print(f"✅ Layout created: {layout_path_3}")

    from machineconfig.cluster.sessions_managers.helpers.enhanced_command_runner import enhanced_zellij_session_start
    enhanced_zellij_session_start(session_name="tmp", layout_path=layout_path_3)
