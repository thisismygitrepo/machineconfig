#!/usr/bin/env python3
"""
Type definitions for the standardized layout configuration schema.
This module defines the data structures that match the layout.json schema.
"""

from typing import TypedDict, List, Literal, NotRequired


class TabConfig(TypedDict):
    """Configuration for a single tab in a layout."""

    tabName: str
    startDir: str
    command: str
    tabWeight: NotRequired[int]


class LayoutConfig(TypedDict):
    """Configuration for a complete layout with its tabs."""

    layoutName: str
    layoutTabs: List[TabConfig]


class LayoutsFile(TypedDict):
    """Complete layout file structure."""

    version: str
    layouts: List[LayoutConfig]


def serialize_layouts_to_file(layouts: list[LayoutConfig], version: Literal["0.1"], path: str):
    """Serialize a LayoutConfig to a JSON string."""
    import json
    layout_file: LayoutsFile = {
        "version": version,
        "layouts": layouts,
    }
    # add "$schema" key pointing to https://bit.ly/cfglayout
    layout_dict = {
        "$schema": "https://bit.ly/cfglayout",
        **layout_file
    }
    json_string = json.dumps(layout_dict, indent=4)
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(json_string, encoding="utf-8")
        return None
    existing_content_layout: LayoutsFile = json.loads(p.read_text(encoding="utf-8"))
    # policy: if layout with same name exists, replace it. we don't lool at tabConfig differences.
    for a_new_layout in layouts:
        for i, existing_layout in enumerate(existing_content_layout["layouts"]):
            if existing_layout["layoutName"] == a_new_layout["layoutName"]:
                existing_content_layout["layouts"][i] = a_new_layout
                break
        else:
            existing_content_layout["layouts"].append(a_new_layout)
    p.write_text(json.dumps(existing_content_layout, indent=4), encoding="utf-8")
    return None
