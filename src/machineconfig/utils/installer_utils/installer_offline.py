
from pathlib import Path


def export():
    import platform
    import shutil
    # getting os and arch
    os_name = platform.system().lower()
    arch = platform.machine().lower()

    res_root = Path.home().joinpath("tmp_results", f"installer_offline-{os_name}-{arch}")
    if res_root.exists():
        shutil.rmtree(res_root)
    res_root.mkdir(parents=True, exist_ok=True)

    binaries_root = res_root.joinpath("binaries")
    binaries_root.mkdir(parents=True, exist_ok=True)
    configs_root = res_root.joinpath("configs")
    configs_root.mkdir(parents=True, exist_ok=True)

    binaries: list[str] = [
"bat", "cpz", "duckdb", "gitcs", "hyperfine", "lazysql", "procs", "rmz", "tv", "watchexec", "zellij",
"broot", "delta", "fastfetch", "gitui", "jq", "lsd", "rainfrog", "rusty-rain", "uv", "ya", "zoxide",
"btm", "diskonaut", "fd", "glow", "lazydocker", "miniserve", "rg", "starship", "uvx", "yazi",
"cpufetch", "dua", "fzf", "hx", "lazygit", "ouch", "rga", "tere", "viu", "yq"
]

    if platform.system() in ["Linux", "Darwin"]:
        from machineconfig.utils.source_of_truth import LINUX_INSTALL_PATH
        for binary in binaries:
            src = Path(LINUX_INSTALL_PATH).joinpath(binary)
            if src.exists():
                dst = binaries_root.joinpath(binary)
                shutil.copy2(src, dst)
                # print(f"Exported {binary} to {dst}")
            else:
                print(f"Warning: {binary} not found in {LINUX_INSTALL_PATH}, skipping export.")
    elif platform.system() == "Windows":
        from machineconfig.utils.source_of_truth import WINDOWS_INSTALL_PATH
        for binary in binaries:
            src = Path(WINDOWS_INSTALL_PATH).joinpath(binary + ".exe")
            if src.exists():
                dst = binaries_root.joinpath(binary + ".exe")
                shutil.copy2(src, dst)
                # print(f"Exported {binary} to {dst}")
            else:
                print(f"Warning: {binary} not found in {WINDOWS_INSTALL_PATH}, skipping export.")
    else:
        print(f"Unsupported platform: {platform.system()}. No binaries exported.")
    

    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    if CONFIG_ROOT.exists():
        shutil.copytree(CONFIG_ROOT, configs_root, dirs_exist_ok=True)
        print(f"Exported configs from {CONFIG_ROOT} to {configs_root}")
    else:
        print(f"Warning: Config root {CONFIG_ROOT} does not exist, skipping config export.")


def import_binaries_and_configs(zip_path: str, overwrite_configs: bool, overwrite_binaries: bool):
    zip_path_obj = Path(zip_path)
    if not zip_path_obj.exists():
        print(f"Error: Zip file {zip_path} does not exist.")
        return

    # checking if os and arch match
    import platform
    os_name = platform.system().lower()
    arch = platform.machine().lower()
    file_name  = zip_path_obj.stem  # Get the file name without extension
    if os_name not in file_name or arch not in file_name:
        print(f"Error: Zip file name {file_name} does not contain expected OS ({os_name}) and architecture ({arch}). Aborting import.")
        return

    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(zip_path_obj.parent)

    # copy binaries to their respective install locations and configs to config location

    extracted_root = zip_path_obj.parent.joinpath(zip_path_obj.stem)
    binaries_root = extracted_root.joinpath("binaries")
    configs_root = extracted_root.joinpath("configs")

    from machineconfig.utils.source_of_truth import CONFIG_ROOT, LINUX_INSTALL_PATH, WINDOWS_INSTALL_PATH
    import shutil
    if platform.system() in ["Linux", "Darwin"]:
        for binary in binaries_root.iterdir():
            dst = Path(LINUX_INSTALL_PATH).joinpath(binary.name)
            if dst.exists() and not overwrite_binaries:
                print(f"Warning: {dst} already exists and overwrite_binaries is False. Skipping {binary.name}.")
                continue
            shutil.copy2(binary, dst)
            print(f"Imported {binary.name} to {dst}")
    elif platform.system() == "Windows":
        for binary in binaries_root.iterdir():
            dst = Path(WINDOWS_INSTALL_PATH).joinpath(binary.name)
            if dst.exists() and not overwrite_configs:
                print(f"Warning: {dst} already exists and overwrite_binaries is False. Skipping {binary.name}.")
                continue
            shutil.copy2(binary, dst)
            print(f"Imported {binary.name} to {dst}")

    if configs_root.exists():
        shutil.copytree(configs_root, CONFIG_ROOT, dirs_exist_ok=True)
        print(f"Imported configs from {configs_root} to {CONFIG_ROOT}")


def get_app():
    import typer
    app = typer.Typer(help="Installer Offline - Export and Import binaries and configs for offline installation",
    no_args_is_help=True,

    )
    app.command(name="export", help="[e] Export binaries and configs", 
            no_args_is_help=False, )(export)
    app.command(name="e", help="[e] Export binaries and configs", 
            no_args_is_help=False, hidden=True)(export)
    app.command(name="import", help="[i] Import binaries and configs", 
            no_args_is_help=True, )(import_binaries_and_configs)
    app.command(name="i", help="[i] Import binaries and configs", 
            no_args_is_help=True, hidden=True)(import_binaries_and_configs)
    
    return app


if __name__ == "__main__":
    export()
