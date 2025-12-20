#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "machineconfig>=8.37",
#     "textual",
#     "pyperclip",
# ]
# ///

"""Cross-platform PATH explorer with Textual TUI."""

from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from machineconfig.scripts.python.helpers.helper_env.path_manager_backend import get_directory_contents, get_path_entries, get_platform


class DirectoryPreview(Static):
    """Widget to display directory contents."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.border_title = "📂 Directory Preview"

    def update_preview(self, directory: str) -> None:
        """Update the preview with directory contents."""
        if not directory:
            self.update("Select a PATH entry to preview its contents")
            return

        contents = get_directory_contents(directory, max_items=30)
        preview_text = f"[bold cyan]{directory}[/bold cyan]\n\n"
        preview_text += "\n".join(contents)
        self.update(preview_text)


class StatusBar(Static):
    """Status bar to show messages."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.border_title = "ℹ️  Status"

    def show_message(self, message: str, message_type: str = "info") -> None:
        """Display a status message."""
        color = {"info": "cyan", "success": "green", "error": "red", "warning": "yellow"}.get(message_type, "white")
        self.update(f"[{color}]{message}[/{color}]")


class PathExplorerApp(App[None]):
    """A Textual app to explore PATH entries."""

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
    }

    Footer {
        background: $panel;
    }

    #main-container {
        height: 100%;
    }

    #left-panel {
        width: 50%;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    #right-panel {
        width: 50%;
        height: 100%;
        border: solid $accent;
        padding: 1;
    }

    ListView {
        height: 1fr;
        border: solid $accent;
        background: $surface;
    }

    ListView > ListItem {
        padding: 0 1;
    }

    ListView > ListItem.--highlight {
        background: $accent 20%;
    }

    DirectoryPreview {
        height: 1fr;
        border: solid $primary;
        background: $surface;
        padding: 1;
        overflow-y: auto;
    }

    StatusBar {
        height: 3;
        border: solid $success;
        background: $surface;
        padding: 1;
    }

    Label {
        padding: 0 1;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("c", "copy_path", "Copy Path", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.selected_path: str = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        platform_name = get_platform()
        yield Header(show_clock=True)
        
        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield Label(f"🔧 PATH Entries ({platform_name})")
                yield ListView(id="path-list")
                
            with Vertical(id="right-panel"):
                yield DirectoryPreview(id="preview")
                yield StatusBar(id="status")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.title = "PATH Explorer"
        self.sub_title = f"Platform: {get_platform()}"
        self.refresh_path_list()
        self.query_one("#status", StatusBar).show_message("Ready. Select a PATH entry to preview its contents.", "info")

    def refresh_path_list(self) -> None:
        """Refresh the list of PATH entries."""
        list_view = self.query_one("#path-list", ListView)
        list_view.clear()
        
        entries = get_path_entries()
        for entry in entries:
            path = Path(entry)
            exists = path.exists()
            icon = "✅" if exists else "❌"
            item = ListItem(Label(f"{icon} {entry}"))
            item.set_class(exists, "--valid")
            list_view.append(item)
        
        self.query_one("#status", StatusBar).show_message(f"Loaded {len(entries)} PATH entries", "success")

    @on(ListView.Highlighted)
    def handle_highlight(self, event: ListView.Highlighted) -> None:
        """Handle highlighting of a PATH entry (scroll preview)."""
        if event.item is None:
            return
        label = event.item.query_one(Label)
        text = label.render()
        # Remove the icon prefix
        highlighted_path = str(text).split(" ", 1)[1] if " " in str(text) else str(text)
        
        preview = self.query_one("#preview", DirectoryPreview)
        preview.update_preview(highlighted_path)
        
        self.query_one("#status", StatusBar).show_message(f"Previewing: {highlighted_path}", "info")

    @on(ListView.Selected)
    def handle_selection(self, event: ListView.Selected) -> None:
        """Handle selection of a PATH entry (Enter key)."""
        label = event.item.query_one(Label)
        text = label.render()
        # Remove the icon prefix
        self.selected_path = str(text).split(" ", 1)[1] if " " in str(text) else str(text)
        
        preview = self.query_one("#preview", DirectoryPreview)
        preview.update_preview(self.selected_path)
        
        self.query_one("#status", StatusBar).show_message(f"Selected: {self.selected_path}", "success")

    def action_refresh(self) -> None:
        """Refresh the PATH list."""
        self.refresh_path_list()

    def action_copy_path(self) -> None:
        """Copy selected path to clipboard."""
        if not self.selected_path:
            self.query_one("#status", StatusBar).show_message("No PATH entry selected", "warning")
            return        
        # # Try to copy to clipboard
        # try:
        #     import pyperclip
        #     pyperclip.copy(self.selected_path)
        #     self.query_one("#status", StatusBar).show_message(f"Copied to clipboard: {self.selected_path}", "success")
        # except ImportError:
        #     self.query_one("#status", StatusBar).show_message("pyperclip not available. Install it to enable clipboard support.", "warning")


def main() -> None:
    """Run the PATH Explorer TUI."""
    app = PathExplorerApp()
    app.run()


if __name__ == "__main__":
    main()
