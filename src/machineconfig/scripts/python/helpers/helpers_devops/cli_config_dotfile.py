
"""Like yadm and dotter."""

from git import Optional
from machineconfig.profile.create_links_export import ON_CONFLICT_LOOSE, ON_CONFLICT_MAPPER, METHOD_LOOSE, METHOD_MAP
from typing import Annotated, Literal
from pathlib import Path
import typer

from machineconfig.utils.source_of_truth import CONFIG_ROOT
BACKUP_ROOT_PRIVATE = Path.home().joinpath("dotfiles/machineconfig/mapper/files")
BACKUP_ROOT_PUBLIC = Path(CONFIG_ROOT).joinpath("dotfiles/mapper")



def _write_to_user_mapper(section: str, entry_name: str, original_path: Path, self_managed_path: Path, method: Literal["symlink", "copy"], is_contents: bool, os_filter: str) -> Path:
    from machineconfig.profile.create_links import USER_MAPPER_PATH
    mapper_path = USER_MAPPER_PATH
    mapper_path.parent.mkdir(parents=True, exist_ok=True)
    if mapper_path.exists():
        content = mapper_path.read_text(encoding="utf-8")
    else:
        content = "# User-defined config file mappings\n# Created by `d c` CLI tool\n\n"
    home = Path.home()
    original_str = f"~/{original_path.relative_to(home)}" if original_path.is_relative_to(home) else original_path.as_posix()
    self_managed_str = f"~/{self_managed_path.relative_to(home)}" if self_managed_path.is_relative_to(home) else self_managed_path.as_posix()
    entry_dict_parts: list[str] = [f"original = '{original_str}'", f"self_managed = '{self_managed_str}'"]
    if is_contents:
        entry_dict_parts.append("contents = true")
    if method == "copy":
        entry_dict_parts.append("copy = true")
    entry_dict_parts.append(f"os = '{os_filter}'")
    entry_line = f"{entry_name} = {{ {', '.join(entry_dict_parts)} }}"
    section_header = f"[{section}]"
    if section_header in content:
        lines = content.split("\n")
        new_lines: list[str] = []
        in_section = False
        entry_updated = False
        for line in lines:
            if line.strip().startswith("[") and line.strip().endswith("]"):
                if in_section and not entry_updated:
                    new_lines.append(entry_line)
                    entry_updated = True
                in_section = line.strip() == section_header
            if in_section and line.strip().startswith(f"{entry_name} ="):
                new_lines.append(entry_line)
                entry_updated = True
                continue
            new_lines.append(line)
        if in_section and not entry_updated:
            new_lines.append(entry_line)
        content = "\n".join(new_lines)
    else:
        content = content.rstrip() + f"\n\n{section_header}\n{entry_line}\n"
    mapper_path.write_text(content, encoding="utf-8")
    return mapper_path

def record_mapping(orig_path: Path, new_path: Path, method: METHOD_LOOSE, section: str, os_filter: str) -> None:
    entry_name = orig_path.stem.replace(".", "_").replace("-", "_")
    method_resolved = METHOD_MAP[method]
    mapper_file = _write_to_user_mapper(section=section, entry_name=entry_name, original_path=orig_path, self_managed_path=new_path, method=method_resolved, is_contents=False, os_filter=os_filter)
    home = Path.home()
    orig_display = f"~/{orig_path.relative_to(home)}" if orig_path.is_relative_to(home) else orig_path.as_posix()
    new_display = f"~/{new_path.relative_to(home)}" if new_path.is_relative_to(home) else new_path.as_posix()
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    console.print(Panel(f"📝 Mapping recorded in: [cyan]{mapper_file}[/cyan]\n[{section}]\n{entry_name} = {{ original = '{orig_display}', self_managed = '{new_display}', os = '{os_filter}' }}", title="Mapper Entry Saved", border_style="cyan", padding=(1, 2),))


def get_backup_path(orig_path: Path, sensitivity: Literal["private", "v", "public", "b"], destination: Optional[str], shared: bool) -> Path:
    match sensitivity:
        case "private" | "v":
            backup_root = BACKUP_ROOT_PRIVATE
        case "public" | "b":
            backup_root = BACKUP_ROOT_PUBLIC
    if destination is None:
        if shared:
            new_path = backup_root.joinpath("shared").joinpath(orig_path.name)
        else:
            new_path = backup_root.joinpath(orig_path.relative_to(Path.home()))
    else:
        if shared:
            dest_path = Path(destination).expanduser().absolute()
            new_path = dest_path.joinpath("shared").joinpath(orig_path.name)
        else:
            dest_path = Path(destination).expanduser().absolute()
            new_path = dest_path.joinpath(orig_path.name)
    return new_path


def get_original_path_from_backup_path(backup_path: Path, sensitivity: Literal["private", "v", "public", "b"], destination: Optional[str], shared: bool) -> Path:
    match sensitivity:
        case "private" | "v":
            backup_root = BACKUP_ROOT_PRIVATE
        case "public" | "b":
            backup_root = BACKUP_ROOT_PUBLIC
    if destination is None:
        if shared:
            relative_part = backup_path.relative_to(backup_root.joinpath("shared"))
        else:
            relative_part = backup_path.relative_to(backup_root)
        original_path = Path.home().joinpath(relative_part)
    else:
        dest_path = Path(destination).expanduser().absolute()
        if shared:
            relative_part = backup_path.relative_to(dest_path.joinpath("shared"))
        else:
            relative_part = backup_path.relative_to(dest_path)
        original_path = Path.home().joinpath(relative_part)
    return original_path


def register_dotfile(
    file: Annotated[str, typer.Argument(help="file/folder path.")],
    method: Annotated[METHOD_LOOSE, typer.Option(..., "--method", "-m", help="Method to use for linking files")] = "copy",
    on_conflict: Annotated[ON_CONFLICT_LOOSE, typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throw-error",
    sensitivity: Annotated[Literal["private", "v", "public", "b"], typer.Option(..., "--sensitivity", "-s", help="Sensitivity of the config file.")] = "private",
    destination: Annotated[Optional[str], typer.Option("--destination", "-d", help="destination folder (override the default, use at your own risk)")] = None,
    section: Annotated[str, typer.Option("--section", "-se", help="Section name in mapper_dotfiles.toml to record this mapping.")] = "default",
    os_filter: Annotated[str, typer.Option("--os", help="Comma-separated OS list or 'any' to apply everywhere.")] = "any",
    shared: Annotated[bool, typer.Option("--shared", "-sh", help="Whether the config file is shared across destinations directory.")] = False,
    record: Annotated[bool, typer.Option("--record", "-r", help="Record the mapping in user's mapper.toml")] = True,
    ) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from machineconfig.utils.links import symlink_map, copy_map
    console = Console()
    orig_path = Path(file).expanduser().absolute()
    new_path = get_backup_path(orig_path=orig_path, sensitivity=sensitivity, destination=destination, shared=shared)
    if not orig_path.exists() and not new_path.exists():
        console.print(f"[red]Error:[/] Neither original file nor self-managed file exists:\n  Original: {orig_path}\n  Self-managed: {new_path}")
        raise typer.Exit(code=1)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    match method:
        case "copy" | "c":
            try:
                copy_map(config_file_default_path=orig_path, self_managed_config_file_path=new_path, on_conflict=ON_CONFLICT_MAPPER[on_conflict])  # type: ignore[arg-type]
            except Exception as e:
                msg = typer.style("Error: ", fg=typer.colors.RED) + str(e)
                typer.echo(msg)
                typer.Exit(code=1)
                return
        case "symlink" | "s":
            try:
                symlink_map(config_file_default_path=orig_path, self_managed_config_file_path=new_path, on_conflict=ON_CONFLICT_MAPPER[on_conflict])  # type: ignore[arg-type]
            except Exception as e:
                msg = typer.style("Error: ", fg=typer.colors.RED) + str(e)
                typer.echo(msg)
                typer.Exit(code=1)
                return
        case _:
            raise ValueError(f"Unknown method: {method}")
    console.print(Panel("\n".join(["✅ Symbolic link created successfully!", "🔄 Add the following snippet to mapper.toml to persist this mapping:",]), title="Symlink Created", border_style="green", padding=(1, 2),))
    if record:
        record_mapping(orig_path=orig_path, new_path=new_path, method=method, section=section, os_filter=os_filter)


def export_dotfiles(
        pwd: Annotated[str, typer.Argument(..., help="Password for zip encryption")],
        over_internet: Annotated[bool, typer.Option("--over-internet", "-i", help="Use internet-based transfer (wormhole-magic)")] = False,
        over_ssh: Annotated[bool, typer.Option("--over-ssh", "-s", help="Use SSH-based transfer (scp) to a remote machine")] = False,
        ):
    """🔗 Export dotfiles for migration to new machine."""
    if over_ssh:
        code_sample = """ftpx ~/dotfiles user@remote_host:^ -z"""
        print("🔗 Exporting dotfiles via SSH-based transfer (scp).")
        print(f"💡 Run the following command on your local machine to copy dotfiles to the remote machine:\n{code_sample}")
        remote_address = typer.prompt("Enter the remote machine address (user@host) to copy dotfiles to ")
        code_concrete = f"fptx ~/dotfiles {remote_address}:^ -z"
        from machineconfig.utils.code import run_shell_script
        run_shell_script(code_concrete)
    dotfiles_dir = Path.home().joinpath("dotfiles")
    if not dotfiles_dir.exists() or not dotfiles_dir.is_dir():
        print(f"❌ Dotfiles directory does not exist: {dotfiles_dir}")
        raise typer.Exit(code=1)
    dotfiles_zip = Path.home().joinpath("dotfiles.zip")
    if dotfiles_zip.exists():
        dotfiles_zip.unlink()
    import shutil
    zipfile = shutil.make_archive(base_name=str(dotfiles_zip)[:-4], format="zip", root_dir=str(dotfiles_dir), base_dir=".", verbose=False)
    from machineconfig.utils.io import encrypt
    zipfile_enc_bytes = encrypt(
        msg=Path(zipfile).read_bytes(),
        pwd=pwd,
    )
    Path(zipfile).unlink()
    zipfile_enc_path = Path(f"{zipfile}.enc")
    if zipfile_enc_path.exists():
        zipfile_enc_path.unlink()
    zipfile_enc_path.write_bytes(zipfile_enc_bytes)
    print(f"✅ Dotfiles exported to: {zipfile_enc_path}")
    if over_internet:
        # rm ~/dotfiles.zip || true
        # ouch c ~/dotfiles dotfiles.zip
        # # INSECURE OVER INTERNET: uvx wormhole-magic send ~/dotfiles.zip
        raise NotImplementedError("Internet-based transfer not yet implemented.")
    else:
        # devops network share-server --no-auth ./dotfiles.zip
        import machineconfig.scripts.python.helpers.helpers_devops.cli_share_server as cli_share_server
        from  machineconfig.scripts.python.helpers.helpers_network.address import select_lan_ipv4
        localipv4 = select_lan_ipv4(prefer_vpn=False)
        port = 8888
        msg = f"""On the remote machine, run the following:
d c i -u http://{localipv4}:{port} -p {pwd}
"""
        from machineconfig.utils.accessories import display_with_flashy_style
        display_with_flashy_style(msg=msg, title="Remote Machine Instructions",)
        cli_share_server.web_file_explorer(
            path=str(zipfile_enc_path),
            no_auth=True,
            port=port,
            # bind_address="
        )


def import_dotfiles(
        url: Annotated[Optional[str], typer.Option(..., "--url", "-u", help="URL or local path to the encrypted dotfiles zip")] = None,
        pwd: Annotated[Optional[str], typer.Option(..., "--pwd", "-p", help="Password for zip decryption")] = None,
        use_ssh: Annotated[bool, typer.Option("--use-ssh", "-s", help="Use SSH-based transfer (scp) from a remote machine that has dotfiles.")]=False,
        ):  
    # # INSECURE cd $HOME; uvx wormhole-magic receive dotfiles.zip.enc --accept-file
    # ☁️  [bold blue]Method 3: USING INTERNET SECURE SHARE[/bold blue]
    #     [dim]cd ~
    #     cloud copy SHARE_URL . --config ss[/dim]
    if use_ssh:
        print("🔗 Importing dotfiles via SSH-based transfer (scp).")
        code = """fptx $USER@$(hostname):^ ~/dotfiles -z"""
        print(f"💡 Run the following command on the remote machine that has the dotfiles:\n{code}")
        url = typer.prompt("Enter the remote machine address (user@host) to copy dotfiles from ")
        code_concrete = f"fptx {url}:^ ~/dotfiles -z"
        from machineconfig.utils.code import run_shell_script
        run_shell_script(code_concrete)
        print("✅ Dotfiles copied via SSH.")
        return
    if url is None:
        url = typer.prompt("Enter the URL or local path to the encrypted dotfiles zip (e..g 192.168.20.4:8888) ")
    if pwd is None:
        pwd = typer.prompt("Enter the password for zip decryption", hide_input=True)
    from machineconfig.scripts.python.helpers.helpers_utils.download import download
    downloaded_file = download(url=url, decompress=False, output_dir=str(Path.home()))
    if downloaded_file is None or not downloaded_file.exists():
        print(f"❌ Failed to download file from URL: {url}")
        raise typer.Exit(code=1)
    zipfile_enc_path = downloaded_file
    from machineconfig.utils.io import decrypt
    zipfile_bytes = decrypt(
        token=zipfile_enc_path.read_bytes(),
        pwd=pwd,
    )
    zipfile_path = Path(str(zipfile_enc_path)[:-4])
    if zipfile_path.exists():
        print(f"⚠️  WARNING: Overwriting existing file: {zipfile_path}")
        zipfile_path.unlink()
    zipfile_path.write_bytes(zipfile_bytes)
    print(f"✅ Decrypted zip file saved to: {zipfile_path}")
    import zipfile
    if Path.home().joinpath("dotfiles").exists():
        print(f"⚠️  WARNING: Overwriting existing directory: {Path.home().joinpath('dotfiles')}")
        import shutil
        shutil.rmtree(Path.home().joinpath("dotfiles"))
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(Path.home().joinpath("dotfiles"))
    print(f"✅ Dotfiles extracted to: {Path.home().joinpath('dotfiles')}")
    zipfile_path.unlink()


def arg_parser() -> None:
    typer.run(register_dotfile)


if __name__ == "__main__":
    arg_parser()
