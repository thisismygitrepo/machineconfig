import os
import shutil
from pathlib import Path
import platform
import subprocess
from typing import Optional


config_dict = {"repo_url": "CUSTOM", "doc": "Cursor", "filename_template_windows_amd_64": "VSCodeSetup-{}.exe", "filename_template_linux_amd_64": "code_{}.deb", "strip_v": True, "exe_name": "cursor"}


def install_linux(version: Optional[str] = None):
    """Install Cursor on Linux systems."""
    _ = version
    # Variables
    home = str(Path.home())
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


def install_windows(version: Optional[str] = None):
    """Install Cursor on Windows systems."""
    _ = version
    home = Path.home()
    downloads_dir = home / "Downloads"

    # Search for Cursor installer in Downloads
    cursor_installer = None
    for pattern in ["**/Cursor*.exe", "**/cursor*.exe"]:
        found = list(downloads_dir.glob(pattern))
        if found:
            cursor_installer = found[0]
            break

    if cursor_installer is None:
        raise FileNotFoundError("Cursor installer (.exe) not found in Downloads folder.")

    print(f"Cursor installer found: {cursor_installer}")

    # Run the installer silently
    try:
        print("Running Cursor installer...")
        subprocess.run([str(cursor_installer), "/SILENT"], capture_output=True, text=True, check=True)
        print("Cursor installer completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Installer failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        # Try alternative silent install flags
        try:
            print("Trying alternative silent install...")
            subprocess.run([str(cursor_installer), "/S"], capture_output=True, text=True, check=True)
            print("Cursor installer completed successfully with /S flag.")
        except subprocess.CalledProcessError as e2:
            print(f"Alternative installer also failed with exit code {e2.returncode}")
            print(f"Error output: {e2.stderr}")
            # If silent install fails, run normally and let user handle it
            print("Running installer in normal mode (user interaction required)...")
            subprocess.run([str(cursor_installer)])

    # Clean up installer file
    try:
        cursor_installer.unlink()
        print(f"Installer file removed: {cursor_installer}")
    except OSError as e:
        print(f"Warning: Could not remove installer file: {e}")

    print("Cursor installation completed. Check your Start Menu or Desktop for Cursor.")


def main(version: Optional[str] = None):
    """Main installation function that handles both Linux and Windows."""
    system = platform.system()

    if system == "Linux":
        install_linux(version)
    elif system == "Windows":
        install_windows(version)
    else:
        raise OSError(f"Unsupported operating system: {system}. This script supports Linux and Windows only.")


if __name__ == "__main__":
    main()
