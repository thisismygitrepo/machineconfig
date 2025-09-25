"""Set Windows Terminal Settings"""

from machineconfig.utils.utils2 import randstr, read_json
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.io_save import save_json
import platform

# from uuid import uuid4
import os
from typing import Any
from rich.console import Console
from rich.panel import Panel


"""
Not to be confused:
* Windows Terminal & Windows Terminal Preview: The latter is the night release version of WT.
* Windows PowerShell & PowerShell: The latter is community developed and is available on all platforms.
* Windows Powershell comes preinstalled with the system, Powershell must be installed separately.
* Lastly, powershell has a preview version as well.
All settings are available on GitHub: https://aka.ms/terminal-profiles-schema
"""


console = Console()
system = platform.system()  # Linux or Windows

assert system == "Windows", "This script is only for Windows."


class TerminalSettings(object):
    def __init__(self):
        # Grabbing Terminal Settings file:
        print(f"\n{'=' * 80}\n🔍 INITIALIZING TERMINAL SETTINGS 🔍\n{'=' * 80}")
        tmp = os.getenv("LOCALAPPDATA")
        if not isinstance(tmp, str):
            print("❌ ERROR: Could not find LOCALAPPDATA environment variable!")
            raise ValueError("Could not find LOCALAPPDATA environment variable.")
        self.path = PathExtended(tmp).joinpath(r"Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json")
        backup_name = f".orig_{randstr()}"
        print(f"📝 Creating backup of original settings as {backup_name}...")
        self.path.copy(append=backup_name)
        print(f"📂 Loading Windows Terminal settings from: {self.path}")
        self.dat: dict[str, Any] = read_json(self.path)
        # Use a plain Python list for profiles
        self.profs = list(self.dat["profiles"]["list"])
        console = Console()
        console.print(Panel(f"✅ Successfully loaded {len(self.profs)} profiles", title="[bold blue]Terminal Settings[/bold blue]", border_style="blue"))

    def save_terminal_settings(self):
        print(f"\n💾 Saving terminal settings to: {self.path}")
        self.dat["profiles"]["list"] = list(self.profs)
        save_json(obj=self.dat, path=self.path, indent=5)
        console.print(Panel("✅ Settings saved successfully!", title="[bold blue]Terminal Settings[/bold blue]", border_style="blue"))

    # ========================= Terminal Settings =========================================
    def update_default_settings(self):
        print("\n⚙️  Updating default terminal settings...")
        # Changing start up settings:
        self.dat["startOnUserLogin"] = True
        self.dat["launchMode"] = "fullscreen"
        self.dat["theme"] = "dark"
        self.dat["focusFollowMouse"] = True
        self.dat["copyOnSelect"] = True
        self.dat["profiles"]["defaults"]["padding"] = "0"
        self.dat["profiles"]["defaults"]["useAcrylic"] = False
        console.print(Panel("✅ Default settings updated", title="[bold blue]Terminal Settings[/bold blue]", border_style="blue"))

    # 1- Customizing Powershell========================================================
    # as opposed to Windows Powershell
    def customize_powershell(self, nerd_font: bool = True):
        print("\n🛠️  Customizing PowerShell profile...")
        pwsh: dict[str, Any] = dict(
            name="PowerShell",
            commandline="pwsh",
            hidden=False,
            opacity=87,
            # guid="{" + str(uuid4()) + "}",  # WT doesn't accept any GUID to identify pwsh
            startingDirectory="%USERPROFILE%",  # "%USERPROFILE%",   # None: inherent from parent process.
        )
        if nerd_font:
            print("🔤 Setting PowerShell font to CaskaydiaCove Nerd Font...")
            pwsh["font"] = dict(face="CaskaydiaCove Nerd Font")  # because oh-my-posh uses glyphs from this font.

        for idx, item in enumerate(self.profs):
            if item["name"] == "PowerShell":
                self.profs[idx].update(pwsh)
                console.print(Panel("✅ PowerShell profile customized successfully", title="[bold blue]Terminal Settings[/bold blue]", border_style="blue"))
                break
        else:
            console.print(Panel("❌ Couldn't customize PowerShell because profile not found, try to install it first.", title="[bold red]Terminal Settings[/bold red]", border_style="red"))

    def make_powershell_default_profile(self):
        print("\n🌟 Setting PowerShell as the default profile...")
        for profile in self.profs:
            if profile["name"] == "PowerShell":
                self.dat["defaultProfile"] = profile["guid"]
                console.print(Panel("✅ PowerShell is now the default profile!", title="[bold blue]Terminal Settings[/bold blue]", border_style="blue"))
                break
        else:
            console.print(Panel("❌ PowerShell profile was not found in the list of profiles and therefore was not made the default.", title="[bold red]Terminal Settings[/bold red]", border_style="red"))


def main():
    print(f"\n{'=' * 80}\n🖥️  WINDOWS TERMINAL SETUP 🖥️\n{'=' * 80}")
    shell = {"powershell": "pwsh.exe", "Windows Powershell": "powershell.exe"}["powershell"].split(".exe", maxsplit=1)[0]
    if shell == "pwsh":
        print("🚀 Starting Windows Terminal configuration with PowerShell...")
        ts = TerminalSettings()
        ts.update_default_settings()
        ts.customize_powershell(nerd_font=True)
        ts.make_powershell_default_profile()
        print("⌨️  Adding keyboard shortcut for pane zoom (ctrl+shift+z)...")
        ts.dat["actions"].append({"command": "togglePaneZoom", "keys": "ctrl+shift+z"})

        ts.save_terminal_settings()
        print(f"\n{'=' * 80}\n✨ WINDOWS TERMINAL SETUP COMPLETE ✨\n{'=' * 80}")
    else:
        error_msg = "❌ ERROR: Only PowerShell is supported, not Windows PowerShell!"
        print(error_msg)
        raise NotImplementedError(error_msg)


if __name__ == "__main__":
    pass
