#!/usr/bin/env python3
"""
Type definitions for the standardized layout configuration schema.
This module defines the data structures that match the layout.json schema.
"""

from typing import TypedDict, List


class TabConfig(TypedDict):
    """Configuration for a single tab in a layout."""

    tabName: str
    startDir: str
    command: str


class LayoutConfig(TypedDict):
    """Configuration for a complete layout with its tabs."""

    layoutName: str
    layoutTabs: List[TabConfig]


class LayoutsFile(TypedDict):
    """Complete layout file structure."""

    version: str
    layouts: List[LayoutConfig]
