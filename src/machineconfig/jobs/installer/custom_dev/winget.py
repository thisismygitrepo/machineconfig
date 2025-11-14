import subprocess
import requests
import tempfile
from pathlib import Path
from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData


r"""
# download latest from
cd $HOME/Downloads
d u "https://github.com/microsoft/winget-cli/releases/download/v1.12.170-preview/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
# this must be run in windows powershell, not in pwsh
Add-AppxPackage .\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle
"""

def is_winget_available() -> bool:
    """
    Check if winget is available in the system PATH.

    Returns:
        bool: True if winget is available, False otherwise
    """
    try:
        result = subprocess.run(["winget", "--version"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def get_latest_winget_release_url() -> Optional[str]:
    """
    Get the download URL for the latest winget .msixbundle file from GitHub releases.

    Returns:
        Optional[str]: URL to the latest .msixbundle file, or None if not found
    """
    try:
        # Get the latest release information from GitHub API
        api_url = "https://api.github.com/repos/microsoft/winget-cli/releases/latest"
        headers = {"Accept": "application/vnd.github.v3+json"}

        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()

        release_data = response.json()

        # Look for .msixbundle file in assets
        for asset in release_data.get("assets", []):
            if asset["name"].endswith(".msixbundle"):
                return asset["browser_download_url"]

        return None
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching latest winget release: {e}")
        return None


def download_file(url: str, destination: Path) -> bool:
    """
    Download a file from URL to destination.

    Args:
        url: URL to download from
        destination: Path where to save the file

    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return True
    except (requests.RequestException, IOError) as e:
        print(f"Error downloading file: {e}")
        return False


def install_msix_package(package_path: Path) -> bool:
    """
    Install an MSIX package using PowerShell.

    Args:
        package_path: Path to the .msixbundle file

    Returns:
        bool: True if installation successful, False otherwise
    """
    try:
        # Use PowerShell to install the MSIX package
        powershell_cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", f"Add-AppxPackage -Path '{package_path}'"]

        result = subprocess.run(
            powershell_cmd,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode == 0:
            print("Winget installed successfully!")
            return True
        else:
            print(f"Installation failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False

    except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
        print(f"Error installing MSIX package: {e}")
        return False


def main(installer_data: InstallerData, version: Optional[str]) -> bool:
    """
    Ensure winget is available on the system. If not available, download and install it.

    Returns:
        bool: True if winget is available (either was already installed or successfully installed),
              False if installation failed
    """
    _ = installer_data
    # First check if winget is already available
    if is_winget_available():
        print("Winget is already available on the system.")
        return True

    print("Winget not found. Attempting to download and install...")

    # Get the latest release URL
    download_url = get_latest_winget_release_url()
    if not download_url:
        print("Could not find the latest winget release URL.")
        return False

    print(f"Found latest winget release: {download_url}")

    # Create temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract filename from URL
        filename = download_url.split("/")[-1]
        if not filename.endswith(".msixbundle"):
            filename = "winget-latest.msixbundle"

        package_path = temp_path / filename

        # Download the package
        print(f"Downloading winget package to {package_path}...")
        if not download_file(download_url, package_path):
            print("Failed to download winget package.")
            return False

        print("Download completed. Installing winget...")

        # Install the package
        if not install_msix_package(package_path):
            print("Failed to install winget package.")
            return False

    # Verify installation
    if is_winget_available():
        print("Winget has been successfully installed and is now available!")
        return True
    else:
        print("Installation completed but winget is still not available. You may need to restart your terminal or add it to PATH.")
        return False
