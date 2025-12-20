#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "machineconfig>=8.37",
#     "textual",
# ]
# ///

"""Textual TUI for navigating `machineconfig` command structure."""


def main() -> None:
    from machineconfig.scripts.python.helpers.helpers_navigator.main_app import CommandNavigatorApp

    CommandNavigatorApp().run()


if __name__ == "__main__":
    main()
