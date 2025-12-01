from machineconfig.jobs.installer.package_groups import PACKAGE_GROUP2NAMES
from machineconfig.utils.schemas.installer.installer_types import InstallerData
from pathlib import Path
from machineconfig.utils.path_extended import DECOMPRESS_SUPPORTED_FORMATS, PathExtended
from machineconfig.utils.source_of_truth import INSTALL_TMP_DIR


def get_group_name_to_repr() -> dict[str, str]:
    # Build category options and maintain a mapping from display text to actual category name
    category_display_to_name: dict[str, str] = {}
    for group_name, group_values in PACKAGE_GROUP2NAMES.items():
        display = f"📦 {group_name:<20}" + "   --   " + f"{'|'.join(group_values):<60}"
        category_display_to_name[display] = group_name
    return category_display_to_name


def handle_installer_not_found(search_term: str, app_apps: list[InstallerData]) -> None:  # type: ignore
    """Handle installer not found with friendly suggestions using fuzzy matching."""
    from difflib import get_close_matches
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    all_names = sorted([inst["appName"] for inst in app_apps])
    name_to_doc = {inst["appName"]: inst["doc"] for inst in app_apps}
    all_descriptions = {f"{inst['appName']}: {inst['doc']}": inst["appName"] for inst in app_apps}

    close_name_matches = get_close_matches(search_term, all_names, n=5, cutoff=0.4)
    close_description_matches = get_close_matches(search_term, list(all_descriptions.keys()), n=5, cutoff=0.4)

    search_lower = search_term.lower()
    substring_matches = [
        inst["appName"]
        for inst in app_apps
        if search_lower in inst["appName"].lower() or search_lower in inst["doc"].lower()
    ]

    ordered_matches: list[str] = list(
        dict.fromkeys(
            close_name_matches
            + [all_descriptions[desc] for desc in close_description_matches]
            + substring_matches
        )
    )
    top_matches = ordered_matches[:10]
    console = Console()

    console.print(f"\n❌ '[red]{search_term}[/red]' was not found.", style="bold")
    if top_matches:
        console.print("🤔 Did you mean one of these?", style="yellow")
        table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
        table.add_column("#", justify="right", width=3)
        table.add_column("Installer", style="green")
        table.add_column("Description", style="dim", overflow="fold")
        for i, match in enumerate(top_matches, 1):
            table.add_row(f"[cyan]{i}[/cyan]", match, name_to_doc.get(match, ""))
        console.print(table)
    else:
        console.print("📋 Here are some available options:", style="blue")
        # Show first 10 installers as examples
        if len(all_names) > 10:
            sample_names = all_names[:10]
        else:
            sample_names = all_names
        table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
        table.add_column("#", justify="right", width=3)
        table.add_column("Installer", style="green")
        table.add_column("Description", style="dim", overflow="fold")
        for i, name in enumerate(sample_names, 1):
            table.add_row(f"[cyan]{i}[/cyan]", name, name_to_doc.get(name, ""))
        console.print(table)
        if len(all_names) > 10:
            console.print(f"   [dim]... and {len(all_names) - 10} more[/dim]")

    panel = Panel(f"[bold blue]💡 Use 'ia' to interactively browse all available installers.[/bold blue]\n[bold blue]💡 Use one of the categories: {list(PACKAGE_GROUP2NAMES.keys())}[/bold blue]", title="[yellow]Helpful Tips[/yellow]", border_style="yellow")
    console.print(panel)


def install_deb_package(downloaded: Path) -> None:
    from rich import print as rprint
    from rich.panel import Panel
    print(f"📦 Installing .deb package: {downloaded}")
    import platform
    import subprocess
    assert platform.system() == "Linux"
    result = subprocess.run(f"sudo nala install -y {downloaded}", shell=True, capture_output=True, text=True)
    success = result.returncode == 0 and result.stderr == ""
    if not success:
        from rich.console import Group
        desc = "Installing .deb"
        sub_panels = []
        if result.stdout:
            sub_panels.append(Panel(result.stdout, title="STDOUT", style="blue"))
        if result.stderr:
            sub_panels.append(Panel(result.stderr, title="STDERR", style="red"))
        group_content = Group(f"❌ {desc} failed\nReturn code: {result.returncode}", *sub_panels)
        rprint(Panel(group_content, title=desc, style="red"))
    print("🗑️  Cleaning up .deb package...")
    if downloaded.is_file():
        downloaded.unlink(missing_ok=True)
    elif downloaded.is_dir():
        import shutil
        shutil.rmtree(downloaded, ignore_errors=True)


def download_and_prepare(download_url: str) -> PathExtended:
    # archive_path = PathExtended(download_url).download(folder=INSTALL_TMP_DIR)
    from machineconfig.scripts.python.helpers.helpers_utils.download import download
    downloaded_object = download(download_url, output_dir=str(INSTALL_TMP_DIR))
    if downloaded_object is None:
        raise ValueError(f"Failed to download from URL: {download_url}")
    archive_path = PathExtended(downloaded_object)
    extracted_path = archive_path
    if extracted_path.is_file() and any(ext in archive_path.suffixes for ext in DECOMPRESS_SUPPORTED_FORMATS):
        extracted_path = archive_path.decompress()
        # print(f"Decompressed {archive_path} to {extracted_path}")
        archive_path.delete(sure=True)
        if extracted_path.is_dir():
            nested_items = list(extracted_path.glob("*"))
            if len(nested_items) == 1:
                nested_path = PathExtended(nested_items[0])
                if nested_path.is_file() and any(ex in nested_path.suffixes for ex in DECOMPRESS_SUPPORTED_FORMATS):
                    extracted_path = nested_path.decompress()
                    nested_path.delete(sure=True)
    elif extracted_path.is_dir() and len([p for p in extracted_path.rglob("*") if not p.name.startswith(".")]) == 1:
        only_file_in = next(extracted_path.glob("*"))
        if only_file_in.is_file() and any(ext in str(only_file_in) for ext in DECOMPRESS_SUPPORTED_FORMATS):  # further decompress
            extracted_path = only_file_in.decompress()
            only_file_in.delete(sure=True)
    return extracted_path
