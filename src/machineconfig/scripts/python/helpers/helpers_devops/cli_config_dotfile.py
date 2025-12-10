
"""Like yadm and dotter."""

from machineconfig.profile.create_links_export import ON_CONFLICT_LOOSE, ON_CONFLICT_MAPPER
from typing import Annotated, Literal
from pathlib import Path
import typer


def write_to_user_mapper(section: str, entry_name: str, original_path: Path, self_managed_path: Path, method: Literal["symlink", "copy"], is_contents: bool) -> Path:
    mapper_path = Path.home().joinpath("dotfiles/machineconfig/mapper.toml")
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


def main(
    file: Annotated[str, typer.Argument(help="file/folder path.")],
    method: Annotated[Literal["symlink", "s", "copy", "c"], typer.Option(..., "--method", "-m", help="Method to use for linking files")] = "copy",
    on_conflict: Annotated[ON_CONFLICT_LOOSE, typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throw-error",
    sensitivity: Annotated[Literal["private", "v", "public", "b"], typer.Option(..., "--sensitivity", "-s", help="Sensitivity of the config file.")] = "private",
    destination: Annotated[str, typer.Option("--destination", "-d", help="destination folder (override the default, use at your own risk)")] = "",
    section: Annotated[str, typer.Option("--section", "-se", help="Section name in mapper.toml to record this mapping.")] = "default",
    shared: Annotated[bool, typer.Option("--shared", "-sh", help="Whether the config file is shared across destinations directory.")] = False,
    record: Annotated[bool, typer.Option("--record", "-r", help="Record the mapping in user's mapper.toml")] = True,
    ) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from machineconfig.utils.links import symlink_map, copy_map
    console = Console()
    orig_path = Path(file).expanduser().absolute()
    match sensitivity:
        case "private" | "v":
            backup_root = Path.home().joinpath("dotfiles/machineconfig/mapper/files")
        case "public" | "b":
            from machineconfig.utils.source_of_truth import CONFIG_ROOT
            backup_root = Path(CONFIG_ROOT).joinpath("dotfiles/mapper")

    if destination == "":
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
    if not orig_path.exists() and not new_path.exists():
        console.print(f"[red]Error:[/] Neither original file nor self-managed file exists:\n  Original: {orig_path}\n  Self-managed: {new_path}")
        raise typer.Exit(code=1)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    match method:
        case "copy" | "c":
            try:
                copy_map(config_file_default_path=orig_path, self_managed_config_file_path=new_path, on_conflict=ON_CONFLICT_MAPPER[on_conflict])  # type: ignore[arg-type]
            except Exception as e:
                typer.echo(f"[red]Error:[/] {e}")
                typer.Exit(code=1)
                return
        case "symlink" | "s":
            try:
                symlink_map(config_file_default_path=orig_path, self_managed_config_file_path=new_path, on_conflict=ON_CONFLICT_MAPPER[on_conflict])  # type: ignore[arg-type]
            except Exception as e:
                typer.echo(f"[red]Error:[/] {e}")
                typer.Exit(code=1)
                return
        case _:
            raise ValueError(f"Unknown method: {method}")
    console.print(Panel("\n".join(["✅ Symbolic link created successfully!", "🔄 Add the following snippet to mapper.toml to persist this mapping:",]), title="Symlink Created", border_style="green", padding=(1, 2),))

    if record:
        entry_name = orig_path.stem.replace(".", "_").replace("-", "_")
        method_resolved: Literal["symlink", "copy"] = "symlink" if method in ("symlink", "s") else "copy"
        mapper_file = write_to_user_mapper(section=section, entry_name=entry_name, original_path=orig_path, self_managed_path=new_path, method=method_resolved, is_contents=False)
        home = Path.home()
        orig_display = f"~/{orig_path.relative_to(home)}" if orig_path.is_relative_to(home) else orig_path.as_posix()
        new_display = f"~/{new_path.relative_to(home)}" if new_path.is_relative_to(home) else new_path.as_posix()
        console.print(Panel(f"📝 Mapping recorded in: [cyan]{mapper_file}[/cyan]\n[{section}]\n{entry_name} = {{ original = '{orig_display}', self_managed = '{new_display}' }}", title="Mapper Entry Saved", border_style="cyan", padding=(1, 2),))


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
