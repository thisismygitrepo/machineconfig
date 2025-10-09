"""
Search bar widget for filtering commands.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Input


class SearchBar(Horizontal):
    """Search bar widget."""

    def compose(self) -> ComposeResult:
        yield Label("🔍 Search: ", classes="search-label")
        yield Input(placeholder="Type to search commands...", id="search-input")