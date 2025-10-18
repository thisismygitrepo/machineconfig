"""
TUI for navigating through machineconfig command structure using Textual.
"""

from machineconfig.scripts.python.helpers_navigator import CommandNavigatorApp


if __name__ == "__main__":
    app = CommandNavigatorApp()
    app.run()
