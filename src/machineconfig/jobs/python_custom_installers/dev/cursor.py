

import os
import shutil
from pathlib import Path
import platform
from typing import Optional


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "Cursor",
        "filename_template_windows_amd_64": "VSCodeSetup-{}.exe",
        "filename_template_linux_amd_64": "code_{}.deb",
        "strip_v": True,
        "exe_name": "cursor"
}


def main(version: Optional[str] = None):
    _ = version
    assert platform.system() == "Linux", "This script is intended for Linux systems only."
    # assert flvour is debiean/mint or ubuntu, "This script is intended for Debian-based systems only."
    # Variables
    # username = os.getenv("USER")
    home = str(Path.home())
    # appimage_src = f"{home}/Downloads/Cursor-0.48.8-x86_64.AppImage"
    # search for anything that has Cursor in the name and ends with .AppImage
    appimage_src = next(Path(home).joinpath("Downloads").glob("**/Cursor*.AppImage"), None)
    if appimage_src is None:
        raise FileNotFoundError("Cursor AppImage not found in Downloads folder.")
    else:
        print(f"Cursor AppImage found: {appimage_src}")
    appimage_dest = f"{home}/.local/bin/cursor"
    desktop_file = f"{home}/.local/share/applications/cursor.desktop"
    icon_path = f"{home}/.local/share/icons/cursor.png"  # Optional: set only if icon exists

    # Step 1: Move AppImage
    os.makedirs(f"{home}/.local/bin", exist_ok=True)
    if not os.path.exists(appimage_dest):
        shutil.move(appimage_src, appimage_dest)
    os.chmod(appimage_dest, 0o755)

    # Step 2: Create .desktop file
    os.makedirs(f"{home}/.local/share/applications", exist_ok=True)
    icon_line = f"Icon={icon_path}" if os.path.exists(icon_path) else "Icon=cursor"

    desktop_content = f"""[Desktop Entry]
Name=Cursor
Comment=Code editor based on VSCode
Exec={appimage_dest}
{icon_line}
Terminal=false
Type=Application
Categories=Development;IDE;
"""
    with open(desktop_file, "w") as f:
        f.write(desktop_content)
    # Step 3: Make the .desktop file executable
    os.chmod(desktop_file, 0o755)
    # Step 4: Update desktop database (optional, usually not needed)
    os.system(f"update-desktop-database {home}/.local/share/applications")
    print("Cursor is now available from the start menu.")


if __name__ == "__main__":
    main()
