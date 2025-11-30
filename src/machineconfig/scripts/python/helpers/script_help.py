
from typing import Literal


def list_available_scripts(where: Literal["all", "a", "private", "p", "public", "b", "library", "l", "dynamic", "d", "custom", "c"]) -> None:
    from pathlib import Path
    from machineconfig.utils.source_of_truth import CONFIG_ROOT, LIBRARY_ROOT, DEFAULTS_PATH

    private_root = Path.home().joinpath("dotfiles/scripts")
    public_root = CONFIG_ROOT.joinpath("scripts")
    library_root = LIBRARY_ROOT.joinpath("jobs", "scripts")

    def get_custom_roots() -> list[Path]:
        custom_roots: list[Path] = []
        if DEFAULTS_PATH.is_file():
            from configparser import ConfigParser
            config = ConfigParser()
            config.read(DEFAULTS_PATH)
            if config.has_section("general") and config.has_option("general", "scripts"):
                custom_dirs = config.get("general", "scripts").split(",")
                for custom_dir in custom_dirs:
                    custom_path = Path(custom_dir.strip()).expanduser().resolve()
                    if custom_path.is_dir():
                        custom_roots.append(custom_path)
        return custom_roots

    locations: dict[str, Path | str] = {}
    match where:
        case "all" | "a":
            locations = {"private": private_root, "public": public_root, "library": library_root}
            for idx, custom in enumerate(get_custom_roots()): locations[f"custom_{idx}"] = custom
            locations["dynamic"] = "https://github.com/thisismygitrepo/machineconfig/tree/main/src/machineconfig/jobs/scripts_dynamic"
        case "private" | "p":
            locations = {"private": private_root}
        case "public" | "b":
            locations = {"public": public_root}
        case "library" | "l":
            locations = {"library": library_root}
        case "dynamic" | "d":
            locations = {"dynamic": "https://github.com/thisismygitrepo/machineconfig/tree/main/src/machineconfig/jobs/scripts_dynamic"}
        case "custom" | "c":
            for idx, custom in enumerate(get_custom_roots()): locations[f"custom_{idx}"] = custom

    def _print_files_by_type(files: list[str]) -> None:
        categories: dict[str, list[str]] = {".py": [], ".sh": [], ".ps1": [], ".cmd": [], ".bat": [], "other": []}
        for f in files:
            ext = Path(f).suffix.lower() if "." in str(f) else ""
            if ext in categories: categories[ext].append(str(f))
            else: categories["other"].append(str(f))
        for ext, cat_files in categories.items():
            if cat_files:
                label = ext if ext else "other"
                print(f"    [{label}]")
                for cf in sorted(cat_files): print(f"      • {cf}")

    for loc_name, loc_path in locations.items():
        print(f"\n📁 {loc_name.upper()} ({loc_path}):")
        print("-" * 60)
        if isinstance(loc_path, Path):
            if loc_path.is_dir():
                files = [f for f in loc_path.rglob("*") if f.is_file() and f.suffix in (".py", ".sh", ".ps1", ".bat", ".cmd", "")]
                if files:
                    relative_files = [str(f.relative_to(loc_path)) for f in files]
                    _print_files_by_type(relative_files)
                else:
                    print("  (empty)")
            else:
                print("  ⚠️  Directory does not exist")
        else:
            api_url = "https://api.github.com/repos/thisismygitrepo/machineconfig/contents/src/machineconfig/jobs/scripts_dynamic"
            try:
                import requests
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    items = response.json()
                    files = [item["name"] for item in items if item["type"] == "file"]
                    _print_files_by_type(files)
                else:
                    print(f"  ⚠️  Could not fetch from GitHub (status: {response.status_code})")
            except Exception as e:
                print(f"  ⚠️  Could not fetch from GitHub: {e}")