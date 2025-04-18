"""Set Windows Terminal Settings
"""

from crocodile.core import randstr, List as L
from crocodile.file_management import P, Read, Save
import crocodile.environment as env
from machineconfig.utils.utils import LIBRARY_ROOT
from uuid import uuid4
import os
from typing import Any


"""
Not to be confused:
* Windows Terminal & Windows Terminal Preview: The latter is the night release version of WT.
* Windows PowerShell & PowerShell: The latter is community developed and is available on all platforms.
* Windows Powershell comes preinstalled with the system, Powershell must be installed separately.
* Lastly, powershell has a preview version as well.
All settings are available on GitHub: https://aka.ms/terminal-profiles-schema
"""


assert env.system == 'Windows', 'This script is only for Windows.'


class TerminalSettings(object):
    def __init__(self):
        # Grabbing Terminal Settings file:
        print(f"\n{'='*80}\n🔍 INITIALIZING TERMINAL SETTINGS 🔍\n{'='*80}")
        tmp = os.getenv("LOCALAPPDATA")
        if not isinstance(tmp, str):
            print("❌ ERROR: Could not find LOCALAPPDATA environment variable!")
            raise ValueError("Could not find LOCALAPPDATA environment variable.")
        self.path = P(tmp).joinpath(r"Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json")
        backup_name = f".orig_{randstr()}"
        print(f"📝 Creating backup of original settings as {backup_name}...")
        self.path.copy(append=backup_name)
        print(f"📂 Loading Windows Terminal settings from: {self.path}")
        self.dat: dict[str, Any] = Read.json(self.path)
        self.profs = L(self.dat["profiles"]["list"])
        print(f"✅ Successfully loaded {len(self.profs)} profiles\n{'-'*80}")

    def save_terminal_settings(self):
        print(f"\n💾 Saving terminal settings to: {self.path}")
        self.dat["profiles"]["list"] = list(self.profs)
        Save.json(obj=self.dat, path=self.path, indent=5)
        print(f"✅ Settings saved successfully!\n{'-'*80}")

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
        print(f"✅ Default settings updated\n{'-'*80}")

    # 1- Customizing Powershell========================================================
    # as opposed to Windows Powershell
    def customize_powershell(self, nerd_font: bool=True):
        print("\n🛠️  Customizing PowerShell profile...")
        pwsh: dict[str, Any] = dict(name="PowerShell",
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
                self.profs.list[idx].update(pwsh)
                print(f"✅ PowerShell profile customized successfully\n{'-'*80}")
                break
        else:
            print(f"❌ Couldn't customize PowerShell because profile not found, try to install it first.\n{'-'*80}")

    def make_powershell_default_profile(self):
        print("\n🌟 Setting PowerShell as the default profile...")
        for profile in self.profs:
            if profile["name"] == "PowerShell":
                self.dat["defaultProfile"] = profile["guid"]
                print(f"✅ PowerShell is now the default profile!\n{'-'*80}")
                break
        else: 
            print(f"❌ PowerShell profile was not found in the list of profiles and therefore was not made the default.\n{'-'*80}")

    def add_croshell(self):
        print("\n🐊 Adding croshell profile...")
        croshell = dict(name="croshell",
                        guid="{" + str(uuid4()) + "}",
                        # commandline=f"powershell.exe -Command \"{activate} ipython -i -c 'from crocodile.toolbox import *'\"",
                        commandline=f'powershell.exe -Command "{LIBRARY_ROOT.as_posix()}/scripts/windows/croshell.ps1"',
                        startingDirectory="%USERPROFILE%",  # "%USERPROFILE%",   # None: inherent from parent process.
                        )
        # startingDirectory = None means: inheret from parent process, which will is the default, which point to /System32
        # Launching a new profile with ctr+shift+2 is equivalent to: wt --profile croshell -d . --new-tab
        for profile in self.profs:
            if profile["name"] == "croshell":
                profile.update(croshell)
                print(f"✅ Updated existing croshell profile\n{'-'*80}")
                break
        else: 
            self.profs.append(croshell)
            print(f"✅ Added new croshell profile\n{'-'*80}")

    def add_ubuntu(self):
        print("\n🐧 Adding Ubuntu WSL profile...")
        # Add Ubunto if it is not there.
        ubuntu = dict(name="Ubuntu",
                      commandline="wsl -d Ubuntu -- cd ~",
                      hidden=False,
                      guid="{" + str(uuid4()) + "}",
                      startingDirectory="%USERPROFILE%",  # "%USERPROFILE%",   # None: inherent from parent process.
                      )
        if self.profs.filter(lambda x: x["name"] == "Ubuntu").__len__() < 1:
            self.profs.append(ubuntu)
            print(f"✅ Added Ubuntu WSL profile\n{'-'*80}")
        else:
            print(f"ℹ️ Ubuntu profile already exists\n{'-'*80}")

    def standardize_profiles_order(self):
        print("\n🔄 Standardizing profile order...")
        # Changing order of profiles:
        others = []
        pwsh = croshell = ubuntu = wpwsh = cmd = azure = None
        for profile in self.profs:
            name = profile["name"]
            if name == "PowerShell": pwsh = profile
            elif name == "croshell": croshell = profile
            elif name == "Ubuntu": ubuntu = profile
            elif name == "Windows PowerShell": wpwsh = profile
            elif name == "Command Prompt": cmd = profile
            elif name == "Azure Cloud Shell": azure = profile
            else: others.append(profile)
        self.profs = L([item for item in [pwsh, croshell, ubuntu, wpwsh, cmd, azure] + others if item is not None])
        print(f"✅ Profile order standardized\n{'-'*80}")


def main():
    print(f"\n{'='*80}\n🖥️  WINDOWS TERMINAL SETUP 🖥️\n{'='*80}")
    shell = {"powershell": "pwsh.exe", "Windows Powershell": "powershell.exe"}["powershell"].split(".exe", maxsplit=1)[0]
    if shell == "pwsh":
        print("🚀 Starting Windows Terminal configuration with PowerShell...")
        ts = TerminalSettings()
        ts.update_default_settings()
        ts.customize_powershell(nerd_font=True)

        ts.make_powershell_default_profile()
        ts.add_croshell()
        ts.add_ubuntu()
        ts.standardize_profiles_order()
        
        print("⌨️  Adding keyboard shortcut for pane zoom (ctrl+shift+z)...")
        ts.dat['actions'].append({'command': 'togglePaneZoom', 'keys': 'ctrl+shift+z'})
        
        ts.save_terminal_settings()
        print(f"\n{'='*80}\n✨ WINDOWS TERMINAL SETUP COMPLETE ✨\n{'='*80}")
    else:
        error_msg = "❌ ERROR: Only PowerShell is supported, not Windows PowerShell!"
        print(error_msg)
        raise NotImplementedError(error_msg)


if __name__ == '__main__':
    pass
