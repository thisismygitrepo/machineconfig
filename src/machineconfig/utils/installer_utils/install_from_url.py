

import platform
from urllib.parse import urlparse

import typer
from typing import TYPE_CHECKING, Optional, TypeAlias, cast

from machineconfig.utils.installer_utils.installer_class import install_deb_package
from machineconfig.utils.installer_utils.installer_locator_utils import find_move_delete_linux, find_move_delete_windows
from machineconfig.utils.path_extended import DECOMPRESS_SUPPORTED_FORMATS, PathExtended
from machineconfig.utils.source_of_truth import INSTALL_TMP_DIR, INSTALL_VERSION_ROOT

if TYPE_CHECKING:
    from rich.console import Console

SUPPORTED_GITHUB_HOSTS = {"github.com", "www.github.com"}

GitHubAsset: TypeAlias = dict[str, object]
GitHubRelease: TypeAlias = dict[str, object]


def _extract_repo_name(github_url: str) -> str:
    parsed = urlparse(github_url)
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return ""
    owner, repo = parts[0], parts[1]
    if repo == "":
        return ""
    return f"{owner}/{repo}"


def _fetch_latest_release(repo_name: str) -> Optional[GitHubRelease]:
    import json
    import requests
    try:
        response = requests.get(f"https://api.github.com/repos/{repo_name}/releases/latest", timeout=30)
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    try:
        data = response.json()
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return cast(GitHubRelease, data)


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


def _derive_tool_name(repo_name: str, asset_name: str) -> str:
    repo_segment = repo_name.split("/", maxsplit=1)[-1]
    repo_clean = repo_segment.replace(".git", "").lower()
    repo_filtered = "".join(char for char in repo_clean if char.isalnum())
    if repo_filtered:
        return repo_filtered
    asset_clean = asset_name.lower()
    asset_filtered = "".join(char for char in asset_clean if char.isalnum())
    if asset_filtered:
        return asset_filtered
    return "githubapp"


def _download_and_prepare(download_url: str) -> PathExtended:
    archive_path = PathExtended(download_url).download(folder=INSTALL_TMP_DIR)
    extracted_path = archive_path
    if extracted_path.suffix in DECOMPRESS_SUPPORTED_FORMATS:
        extracted_path = archive_path.decompress()
        archive_path.delete(sure=True)
        if extracted_path.is_dir():
            nested_items = list(extracted_path.glob("*"))
            if len(nested_items) == 1:
                nested_path = PathExtended(nested_items[0])
                if nested_path.suffix in DECOMPRESS_SUPPORTED_FORMATS:
                    extracted_path = nested_path.decompress()
                    nested_path.delete(sure=True)
    return extracted_path


def _finalize_install(repo_name: str, asset_name: str, version: str, extracted_path: PathExtended, console: "Console") -> None:
    from rich.panel import Panel

    if extracted_path.suffix == ".deb":
        install_deb_package(extracted_path)
        tool_name_deb = _derive_tool_name(repo_name, asset_name)
        INSTALL_VERSION_ROOT.joinpath(tool_name_deb).parent.mkdir(parents=True, exist_ok=True)
        INSTALL_VERSION_ROOT.joinpath(tool_name_deb).write_text(version, encoding="utf-8")
        console.print(Panel(f"Installed Debian package for [green]{tool_name_deb}[/green]", title="✅ Complete", border_style="green"))
        return
    system_name = platform.system()
    tool_name = _derive_tool_name(repo_name, asset_name)
    rename_target = f"{tool_name}.exe" if system_name == "Windows" else tool_name
    try:
        if system_name == "Windows":
            installed_path = find_move_delete_windows(downloaded_file_path=extracted_path, exe_name=tool_name, delete=True, rename_to=rename_target)
        elif system_name in {"Linux", "Darwin"}:
            installed_path = find_move_delete_linux(downloaded=extracted_path, tool_name=tool_name, delete=True, rename_to=rename_target)
        else:
            console.print(Panel(f"Unsupported operating system: {system_name}", title="❌ Error", border_style="red"))
            raise typer.Exit(1)
    except IndexError:
        if system_name == "Windows":
            installed_path = find_move_delete_windows(downloaded_file_path=extracted_path, exe_name=None, delete=True, rename_to=rename_target)
        elif system_name in {"Linux", "Darwin"}:
            installed_path = find_move_delete_linux(downloaded=extracted_path, tool_name="", delete=True, rename_to=rename_target)
        else:
            raise
    INSTALL_VERSION_ROOT.joinpath(tool_name).parent.mkdir(parents=True, exist_ok=True)
    INSTALL_VERSION_ROOT.joinpath(tool_name).write_text(version, encoding="utf-8")
    console.print(Panel(f"Installed [green]{tool_name}[/green] to {installed_path}\nVersion: {version}", title="✅ Complete", border_style="green"))


def install_from_github_url(github_url: str) -> None:
    from machineconfig.utils.options import choose_from_options
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    repo_name = _extract_repo_name(github_url)
    if repo_name == "":
        console.print(Panel(f"Invalid GitHub URL: {github_url}", title="❌ Error", border_style="red"))
        raise typer.Exit(1)
    console.print(Panel(f"Fetching latest release for [green]{repo_name}[/green]", title="🌐 GitHub", border_style="blue"))
    release_raw = _fetch_latest_release(repo_name)
    if not release_raw:
        console.print(Panel("No releases available for this repository.", title="❌ Error", border_style="red"))
        raise typer.Exit(1)
    release = release_raw
    assets_value = release.get("assets", [])
    assets: list[GitHubAsset] = []
    if isinstance(assets_value, list):
        for asset in assets_value:
            if isinstance(asset, dict):
                typed_asset: GitHubAsset = {}
                name_value = asset.get("name")
                url_value = asset.get("browser_download_url")
                size_value = asset.get("size")
                content_value = asset.get("content_type")
                if isinstance(name_value, str):
                    typed_asset["name"] = name_value
                if isinstance(url_value, str):
                    typed_asset["browser_download_url"] = url_value
                if isinstance(size_value, int):
                    typed_asset["size"] = size_value
                if isinstance(content_value, str):
                    typed_asset["content_type"] = content_value
                assets.append(typed_asset)
    if not assets:
        console.print(Panel("No downloadable assets found in the latest release.", title="❌ Error", border_style="red"))
        raise typer.Exit(1)
    binary_assets = assets
    selection_pool = binary_assets if binary_assets else assets
    if not selection_pool:
        console.print(Panel("No assets available for installation.", title="❌ Error", border_style="red"))
        raise typer.Exit(1)
    options_map: dict[str, GitHubAsset] = {}
    for asset in selection_pool:
        name = asset.get("name")
        download_url = asset.get("browser_download_url")
        if not isinstance(name, str) or not isinstance(download_url, str) or name == "" or download_url == "":
            continue
        size_value = asset.get("size")
        size = size_value if isinstance(size_value, int) else 0
        label = f"{name} [{_format_size(size)}]"
        options_map[label] = asset
    if not options_map:
        console.print(Panel("Release assets lack download URLs.", title="❌ Error", border_style="red"))
        raise typer.Exit(1)
    selection_label = choose_from_options(options=list(options_map.keys()), msg="Select a release asset", multi=False, header="📦 GitHub Release Assets", fzf=True)
    selected_asset = options_map[selection_label]
    download_url_value = selected_asset.get("browser_download_url")
    asset_name_value = selected_asset.get("name")
    if not isinstance(download_url_value, str) or download_url_value == "":
        console.print(Panel("Selected asset lacks a download URL.", title="❌ Error", border_style="red"))
        raise typer.Exit(1)
    asset_name = asset_name_value if isinstance(asset_name_value, str) else "github_binary"
    version_value = release.get("tag_name")
    version = version_value if isinstance(version_value, str) and version_value != "" else "latest"
    console.print(Panel(f"Downloading [cyan]{asset_name}[/cyan]", title="⬇️ Download", border_style="magenta"))
    extracted_path = _download_and_prepare(download_url_value)
    _finalize_install(repo_name=repo_name, asset_name=asset_name, version=version, extracted_path=extracted_path, console=console)


def install_from_binary_url(binary_url: str) -> None:
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    parsed = urlparse(binary_url)
    asset_candidate = parsed.path.split("/")[-1] if parsed.path else ""
    asset_name = asset_candidate if asset_candidate != "" else "binary_asset"
    host = parsed.netloc if parsed.netloc != "" else "remote host"
    console.print(Panel(f"Downloading [cyan]{asset_name}[/cyan] from [green]{host}[/green]", title="⬇️ Download", border_style="magenta"))
    extracted_path = _download_and_prepare(binary_url)
    _finalize_install(repo_name="", asset_name=asset_name, version="latest", extracted_path=extracted_path, console=console)
