#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "machineconfig>=8.37",
#     "textual",
#     "pyperclip",
# ]
# ///



import os
import platform
from collections.abc import Mapping
from typing import Final

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static


VALUE_PREVIEW_LIMIT: Final[int] = 4096
SUMMARY_LIMIT: Final[int] = 96


def truncate_text(text: str, limit: int) -> tuple[str, int]:
    length = len(text)
    if length <= limit:
        return text, 0
    return text[:limit], length - limit


def format_summary(env_key: str, env_value: str, limit: int) -> str:
    sanitized = env_value.replace("\n", "\\n").replace("\t", "\\t")
    preview, remainder = truncate_text(sanitized, limit)
    if preview == "":
        base = f"{env_key} = <empty>"
    else:
        base = f"{env_key} = {preview}"
    if remainder == 0:
        return base
    return f"{base}... (+{remainder} chars)"


def collect_environment(env: Mapping[str, str]) -> list[tuple[str, str]]:
    return sorted(env.items(), key=lambda pair: pair[0].lower())


class EnvListItem(ListItem):
    def __init__(self, env_key: str, summary: str) -> None:
        super().__init__(Label(summary))
        self._env_key = env_key

    def env_key(self) -> str:
        return self._env_key


class EnvValuePreview(Static):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.border_title = "Environment Value"

    def show_value(self, env_key: str, env_value: str) -> None:
        preview, remainder = truncate_text(env_value, VALUE_PREVIEW_LIMIT)
        text = Text()
        text.append(f"{env_key}\n\n", style="bold cyan")
        if preview == "":
            text.append("<empty>", style="dim")
        else:
            text.append(preview)
        if remainder > 0:
            text.append(f"\n... truncated {remainder} characters", style="yellow")
        self.update(text)


class StatusBar(Static):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.border_title = "Status"

    def show_message(self, message: str, level: str) -> None:
        palette = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }
        color = palette.get(level, "white")
        self.update(f"[{color}]{message}[/{color}]")


class EnvExplorerApp(App[None]):
    CSS = """
    Screen { background: $surface; }
    Header { background: $primary; color: $text; }
    Footer { background: $panel; }
    #main-container { height: 100%; }
    #left-panel { width: 50%; height: 100%; border: solid $primary; padding: 1; }
    #right-panel { width: 50%; height: 100%; border: solid $accent; padding: 1; }
    ListView { height: 1fr; border: solid $accent; background: $surface; }
    ListView > ListItem { padding: 0 1; }
    EnvValuePreview { height: 1fr; border: solid $primary; background: $surface; padding: 1; overflow-y: auto; }
    StatusBar { height: 3; border: solid $success; background: $surface; padding: 1; }
    Label { padding: 0 1; height: auto; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("c", "copy_entry", "Copy", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._env_pairs: list[tuple[str, str]] = []
        self._env_lookup: dict[str, str] = {}
        self._selected_key: str = ""

    def compose(self) -> ComposeResult:
        platform_name = platform.system()
        yield Header(show_clock=True)
        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield Label(f"🌐 Environment Variables ({platform_name})")
                yield ListView(id="env-list")
            with Vertical(id="right-panel"):
                yield EnvValuePreview(id="preview")
                yield StatusBar(id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Environment Explorer"
        self.sub_title = f"Platform: {platform.system()}"
        self._reload_environment()
        self._status().show_message("Ready. Select a variable to preview its value.", "info")

    def _reload_environment(self) -> None:
        self._env_pairs = collect_environment(os.environ)
        self._env_lookup = dict(self._env_pairs)
        self._populate_list()

    def _populate_list(self) -> None:
        list_view = self.query_one("#env-list", ListView)
        list_view.clear()
        for env_key, env_value in self._env_pairs:
            summary = format_summary(env_key, env_value, SUMMARY_LIMIT)
            list_view.append(EnvListItem(env_key, summary))
        self._status().show_message(f"Loaded {len(self._env_pairs)} environment variables.", "success")

    def _status(self) -> StatusBar:
        return self.query_one("#status", StatusBar)

    def _preview(self) -> EnvValuePreview:
        return self.query_one("#preview", EnvValuePreview)

    @on(ListView.Highlighted)
    def handle_highlight(self, event: ListView.Highlighted) -> None:
        if not isinstance(event.item, EnvListItem):
            return
        env_key = event.item.env_key()
        env_value = self._env_lookup.get(env_key, "")
        self._preview().show_value(env_key, env_value)
        self._status().show_message(f"Previewing {env_key}", "info")

    @on(ListView.Selected)
    def handle_selection(self, event: ListView.Selected) -> None:
        if not isinstance(event.item, EnvListItem):
            return
        env_key = event.item.env_key()
        self._selected_key = env_key
        env_value = self._env_lookup.get(env_key, "")
        self._preview().show_value(env_key, env_value)
        self._status().show_message(f"Selected {env_key}", "success")

    def action_refresh(self) -> None:
        self._reload_environment()
        self._status().show_message("Environment reloaded.", "success")

    def action_copy_entry(self) -> None:
        if self._selected_key == "":
            self._status().show_message("No variable selected.", "warning")
            return
        env_value = self._env_lookup.get(self._selected_key, "")
        payload = f"{self._selected_key}={env_value}"
        try:
            import pyperclip  # type: ignore[import]

            pyperclip.copy(payload)
            self._status().show_message(f"Copied {self._selected_key} to clipboard.", "success")
        except ImportError:
            self._status().show_message("pyperclip unavailable. Install it for clipboard support.", "warning")


def main() -> None:
    app = EnvExplorerApp()
    app.run()


if __name__ == "__main__":
    main()
