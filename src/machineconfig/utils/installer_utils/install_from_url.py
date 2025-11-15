

import platform
from typing import TYPE_CHECKING, Optional

from machineconfig.utils.installer_utils.installer_helper import install_deb_package, download_and_prepare
from machineconfig.utils.installer_utils.installer_locator_utils import find_move_delete_linux, find_move_delete_windows
from machineconfig.utils.installer_utils.github_release_bulk import (
    get_repo_name_from_url,
    fetch_github_release_data,
    extract_release_info,
    AssetInfo,
)
from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.source_of_truth import INSTALL_VERSION_ROOT

if TYPE_CHECKING:
    from rich.console import Console

SUPPORTED_GITHUB_HOSTS = {"github.com", "www.github.com"}


def _format_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return "0 B"
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(size_bytes)
    index = 0
    while value >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1
    return f"{value:.1f} {units[index]}"


def _derive_tool_name(repo_name: str, asset_name: Optional[str]) -> Optional[str]:
    repo_segment = repo_name.split("/", maxsplit=1)[-1]
    repo_clean = repo_segment.replace(".git", "").lower()
    repo_filtered = "".join(char for char in repo_clean if char.isalnum())
    if repo_filtered:
        return repo_filtered
    if asset_name is None:
        return None
    asset_clean = asset_name.lower()
    asset_filtered = "".join(char for char in asset_clean if char.isalnum())
    if asset_filtered:
        return asset_filtered
    return None


def _finalize_install(repo_name: str, asset_name: Optional[str], version: str, extracted_path: PathExtended, console: "Console") -> None:
    from rich.panel import Panel
    if extracted_path.suffix == ".deb":
        install_deb_package(extracted_path)
        tool_name_deb = _derive_tool_name(repo_name, asset_name)
        if tool_name_deb is not None:
            INSTALL_VERSION_ROOT.joinpath(tool_name_deb).parent.mkdir(parents=True, exist_ok=True)
            INSTALL_VERSION_ROOT.joinpath(tool_name_deb).write_text(version, encoding="utf-8")
        console.print(Panel(f"Installed Debian package for [green]{tool_name_deb}[/green]", title="✅ Complete", border_style="green"))
        return
    system_name = platform.system()
    tool_name = _derive_tool_name(repo_name, asset_name)
    rename_target = f"{tool_name}.exe" if system_name == "Windows" else tool_name
    try:
        if system_name == "Windows":
            installed_path = find_move_delete_windows(downloaded_file_path=extracted_path, tool_name=tool_name, delete=True, rename_to=rename_target)
        elif system_name in {"Linux", "Darwin"}:
            installed_path = find_move_delete_linux(downloaded=extracted_path, tool_name=tool_name, delete=True, rename_to=rename_target)
        else:
            console.print(Panel(f"Unsupported operating system: {system_name}", title="❌ Error", border_style="red"))
            return None
    except IndexError:
        if system_name == "Windows":
            installed_path = find_move_delete_windows(downloaded_file_path=extracted_path, tool_name=None, delete=True, rename_to=rename_target)
        elif system_name in {"Linux", "Darwin"}:
            installed_path = find_move_delete_linux(downloaded=extracted_path, tool_name="", delete=True, rename_to=rename_target)
        else:
            raise
    if tool_name is not None:
        INSTALL_VERSION_ROOT.joinpath(tool_name).parent.mkdir(parents=True, exist_ok=True)
        INSTALL_VERSION_ROOT.joinpath(tool_name).write_text(version, encoding="utf-8")
    console.print(Panel(f"Installed [green]{tool_name}[/green] to {installed_path}\nVersion: {version}", title="✅ Complete", border_style="green"))


def install_from_github_url(github_url: str) -> None:
    from machineconfig.utils.options import choose_from_options
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    repo_info = get_repo_name_from_url(github_url)
    if repo_info is None:
        console.print(Panel(f"Invalid GitHub URL: {github_url}", title="❌ Error", border_style="red"))
        return None
    owner, repo = repo_info
    repo_name = f"{owner}/{repo}"
    console.print(Panel(f"Fetching latest release for [green]{repo_name}[/green]", title="🌐 GitHub", border_style="blue"))
    release_raw = fetch_github_release_data(owner, repo)
    if not release_raw:
        console.print(Panel("No releases available for this repository.", title="❌ Error", border_style="red"))
        return None
    
    release_info = extract_release_info(release_raw)
    if not release_info:
        console.print(Panel("Failed to parse release information.", title="❌ Error", border_style="red"))
        return None
    
    assets = release_info["assets"]
    if not assets:
        console.print(Panel("No downloadable assets found in the latest release.", title="❌ Error", border_style="red"))
        return None
    binary_assets = assets
    selection_pool = binary_assets if binary_assets else assets
    if not selection_pool:
        console.print(Panel("No assets available for installation.", title="❌ Error", border_style="red"))
        return None
    
    # First pass: collect all formatted data and calculate column widths
    asset_data = []
    for asset in selection_pool:
        name = asset["name"]
        download_url = asset["browser_download_url"]
        if name == "" or download_url == "":
            continue
        size = asset["size"]
        download_count = asset.get("download_count", 0)
        created_at = asset.get("created_at", "")
        
        # Format each field
        size_str = f"[{_format_size(size)}]"
        downloads_str = f"{download_count:,}"
        date_str = created_at.split("T")[0] if created_at else "N/A"
        
        asset_data.append({
            "name": name,
            "size_str": size_str,
            "downloads_str": downloads_str,
            "date_str": date_str,
            "asset": asset
        })
    
    # Calculate maximum widths for alignment
    max_name_len = max(len(item["name"]) for item in asset_data) if asset_data else 0
    max_size_len = max(len(item["size_str"]) for item in asset_data) if asset_data else 0
    max_downloads_len = max(len(item["downloads_str"]) for item in asset_data) if asset_data else 0
    
    # Second pass: build aligned labels
    options_map: dict[str, AssetInfo] = {}
    for item in asset_data:
        name_padded = item["name"].ljust(max_name_len)
        size_padded = item["size_str"].ljust(max_size_len)
        downloads_padded = item["downloads_str"].rjust(max_downloads_len)
        
        label = f"{name_padded} {size_padded} | ⬇ {downloads_padded} | 📅 {item['date_str']}"
        options_map[label] = item["asset"]
    
    if not options_map:
        console.print(Panel("Release assets lack download URLs.", title="❌ Error", border_style="red"))
        return None
    selection_label = choose_from_options(options=list(options_map.keys()), msg="Select a release asset", multi=False, header="📦 GitHub Release Assets", tv=True)
    selected_asset = options_map[selection_label]
    download_url_value = selected_asset["browser_download_url"]
    asset_name_value = selected_asset["name"]
    if download_url_value == "":
        console.print(Panel("Selected asset lacks a download URL.", title="❌ Error", border_style="red"))
        return None
    asset_name = asset_name_value if asset_name_value != "" else "github_binary"
    version = release_info["tag_name"] if release_info["tag_name"] != "" else "latest"
    console.print(Panel(f"Downloading [cyan]{asset_name}[/cyan]", title="⬇️ Download", border_style="magenta"))
    extracted_path = download_and_prepare(download_url_value)
    _finalize_install(repo_name=repo_name, asset_name=asset_name, version=version, extracted_path=extracted_path, console=console)


def install_from_binary_url(binary_url: str) -> None:
    from rich.console import Console
    # from rich.panel import Panel
    console = Console()
    # parsed = urlparse(binary_url)
    # asset_candidate = parsed.path.split("/")[-1] if parsed.path else ""
    # asset_name = asset_candidate if asset_candidate != "" else "binary_asset"
    # host = parsed.netloc if parsed.netloc != "" else "remote host"
    # console.print(Panel(f"Downloading from [green]{binary_url}[/green]", title="⬇️ Download", border_style="magenta"))
    extracted_path = download_and_prepare(binary_url)
    _finalize_install(repo_name="", asset_name=None, version="latest", extracted_path=extracted_path, console=console)
