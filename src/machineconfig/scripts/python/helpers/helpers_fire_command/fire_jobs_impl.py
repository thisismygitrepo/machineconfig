"""Pure Python implementation for fire_jobs route command - no typer dependencies."""

from typing import Optional, Callable
from pathlib import Path
from machineconfig.scripts.python.helpers.helpers_fire_command.fire_jobs_args_helper import FireJobArgs

RandStrFunc = Callable[[int], str]


def route(args: FireJobArgs, fire_args: str) -> None:
    """Route execution based on args configuration."""
    from machineconfig.utils.path_helper import get_choice_file
    from machineconfig.utils.accessories import get_repo_root, randstr

    choice_file = get_choice_file(args.path, suffixes=None)
    repo_root = get_repo_root(choice_file)
    print(f"💾 Selected file: {choice_file}.\nRepo root: {repo_root}")

    if args.marimo:
        _handle_marimo(choice_file=choice_file, repo_root=repo_root, randstr_func=randstr)
        return

    kwargs_dict = _prepare_kwargs(args=args, choice_file=choice_file)
    choice_function = _choose_function(args=args, choice_file=choice_file, kwargs_dict=kwargs_dict)
    if isinstance(choice_function, tuple):
        choice_function, choice_file, kwargs_dict = choice_function

    command = _build_command(args=args, choice_file=choice_file, choice_function=choice_function, kwargs_dict=kwargs_dict, repo_root=repo_root, fire_args=fire_args, randstr_func=randstr)
    command = _apply_command_modifiers(args=args, command=command, choice_file=choice_file, repo_root=repo_root, randstr_func=randstr)

    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=command, strict=False)


def _handle_marimo(choice_file: Path, repo_root: Optional[Path], randstr_func: RandStrFunc) -> None:
    """Handle marimo notebook launch."""
    print(f"🧽 Preparing to launch Marimo notebook for `{choice_file}`...")
    tmp_dir = Path.home().joinpath(f"tmp_results/tmp_scripts/marimo/{choice_file.stem}_{randstr_func(10)}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    script = f"""
cd {tmp_dir}
uv run --python 3.14 --with marimo marimo convert {choice_file} -o marimo_nb.py
uv run --project {repo_root} --with marimo marimo edit --host 0.0.0.0 marimo_nb.py
"""
    from machineconfig.utils.code import exit_then_run_shell_script
    print(f"🚀 Launching Marimo notebook for `{choice_file}`...")
    exit_then_run_shell_script(script)


def _prepare_kwargs(args: FireJobArgs, choice_file: Path) -> dict[str, object]:
    """Prepare kwargs dict from args."""
    if choice_file.suffix == ".py":
        from machineconfig.scripts.python.helpers.helpers_fire_command.fire_jobs_args_helper import extract_kwargs
        return extract_kwargs(args)
    return {}


def _choose_function(args: FireJobArgs, choice_file: Path, kwargs_dict: dict[str, object]) -> Optional[str] | tuple[Optional[str], Path, dict[str, object]]:
    """Choose function to run, possibly interactively."""
    if args.choose_function:
        from machineconfig.scripts.python.helpers.helpers_fire_command.fire_jobs_route_helper import choose_function_or_lines
        choice_function, choice_file, kwargs_dict = choose_function_or_lines(choice_file, kwargs_dict)
        return (choice_function, choice_file, kwargs_dict)
    return args.function


def _build_command(args: FireJobArgs, choice_file: Path, choice_function: Optional[str], kwargs_dict: dict[str, object], repo_root: Optional[Path], fire_args: str, randstr_func: RandStrFunc) -> str:
    """Build the execution command."""
    if choice_file.suffix == ".py":
        exe_line = _build_python_exe_line(args=args, choice_file=choice_file, repo_root=repo_root)
        choice_file_adjusted = _adjust_choice_file(args=args, choice_file=choice_file, repo_root=repo_root)

        if args.script or (args.debug and args.choose_function):
            choice_file = _create_import_script(choice_file=choice_file, choice_function=choice_function, kwargs_dict=kwargs_dict, repo_root=repo_root, randstr_func=randstr_func)
            choice_file_adjusted = str(choice_file)

        return _build_final_command(args=args, exe_line=exe_line, choice_file=choice_file, choice_file_adjusted=choice_file_adjusted, choice_function=choice_function, fire_args=fire_args)
    elif choice_file.suffix in (".ps1", ".sh"):
        return f". {choice_file}"
    elif choice_file.suffix == "":
        return str(choice_file)
    else:
        raise NotImplementedError(f"File type {choice_file.suffix} not supported, in the sense that I don't know how to fire it.")


def _build_python_exe_line(args: FireJobArgs, choice_file: Path, repo_root: Optional[Path]) -> str:
    """Build Python execution line."""
    module_line = "-m" if args.module else ""
    with_project = f"--project {repo_root} " if repo_root is not None else ""
    interactive_line = "-i" if args.interactive else ""

    if args.interactive:
        from machineconfig.utils.ve import get_ve_path_and_ipython_profile
        _ve_root_from_file, ipy_profile = get_ve_path_and_ipython_profile(init_path=choice_file)
        if ipy_profile is None:
            ipy_profile = "default"
        ipython_line = f"--no-banner --profile {ipy_profile} "
    else:
        ipython_line = ""

    if args.streamlit:
        from machineconfig.scripts.python.helpers.helpers_fire_command.fire_jobs_route_helper import get_command_streamlit
        interpreter_line = get_command_streamlit(choice_file=choice_file, environment=args.environment, repo_root=repo_root)
    elif args.jupyter:
        interpreter_line = "jupyter-lab"
    else:
        interpreter_line = "python" if not args.interactive else "ipython"

    return f"uv run {with_project} {interpreter_line} {interactive_line} {module_line} {ipython_line}"


def _adjust_choice_file(args: FireJobArgs, choice_file: Path, repo_root: Optional[Path]) -> str:
    """Adjust choice file path for module mode."""
    if args.module and choice_file.suffix == ".py":
        if repo_root is not None:
            return ".".join(Path(choice_file).relative_to(repo_root).parts).replace(".py", "")
        else:
            return ".".join(Path(choice_file).relative_to(Path.cwd()).parts).replace(".py", "")
    return str(choice_file)


def _create_import_script(choice_file: Path, choice_function: Optional[str], kwargs_dict: dict[str, object], repo_root: Optional[Path], randstr_func: RandStrFunc) -> Path:
    """Create a script that imports the module and calls the function."""
    from machineconfig.scripts.python.helpers.helpers_fire_command.file_wrangler import get_import_module_code, wrap_import_in_try_except
    from machineconfig.utils.meta import lambda_to_python_script
    from machineconfig.utils.code import print_code

    import_code = get_import_module_code(str(choice_file))
    import_code_robust = lambda_to_python_script(
        lambda: wrap_import_in_try_except(
            import_line=import_code, pyfile=str(choice_file), repo_root=str(repo_root) if repo_root is not None else None
        ),
        in_global=True,
        import_module=False,
    )
    code_printing = lambda_to_python_script(
        lambda: print_code(code=import_code_robust, lexer="python", desc="import as module code"),
        in_global=True, import_module=False
    )
    print(f"🧩 Preparing import code for module import:\n{import_code}")
    if choice_function is not None:
        calling = f"""res = {choice_function}({("**" + str(kwargs_dict)) if kwargs_dict else ""})"""
    else:
        calling = """# No function selected to call. You can add your code here."""
    new_choice_file = Path.home().joinpath(f"tmp_results/tmp_scripts/python/{Path(choice_file).parent.name}_{Path(choice_file).stem}_{randstr_func(10)}.py")
    new_choice_file.parent.mkdir(parents=True, exist_ok=True)
    new_choice_file.write_text(import_code_robust + "\n" + code_printing + "\n" + calling, encoding="utf-8")
    return new_choice_file


def _build_final_command(args: FireJobArgs, exe_line: str, choice_file: Path, choice_file_adjusted: str, choice_function: Optional[str], fire_args: str) -> str:
    """Build the final command string."""
    if args.debug:
        import platform
        if platform.system() == "Windows":
            return f"{exe_line} -m ipdb {choice_file_adjusted} "
        elif platform.system() in ["Linux", "Darwin"]:
            return f"{exe_line} -m pudb {choice_file_adjusted} "
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported.")
    elif args.module:
        return f"{exe_line} {choice_file_adjusted} "
    elif choice_function is not None and choice_file.suffix == ".py":
        return f"{exe_line} -m fire {choice_file_adjusted} {choice_function} {fire_args}"
    elif args.streamlit:
        if args.holdDirectory:
            return f"{exe_line} {choice_file}"
        else:
            return f"cd {choice_file.parent}\n{exe_line} {choice_file.name}\ncd {Path.cwd()}"
    elif args.cmd:
        return rf""" cd /d {choice_file.parent} & {exe_line} {choice_file.name} """
    elif choice_file.suffix == "":
        return f"{exe_line} {choice_file} {fire_args}"
    else:
        return f"{exe_line} {choice_file} "


def _apply_command_modifiers(args: FireJobArgs, command: str, choice_file: Path, repo_root: Optional[Path], randstr_func: RandStrFunc) -> str:
    """Apply various command modifiers based on args."""
    from rich.panel import Panel
    from rich.console import Console
    from rich.syntax import Syntax

    console = Console()

    if args.cmd:
        new_line = "\n"
        command = rf"""start cmd -Argument "/k {command.replace(new_line, " & ")} " """

    if args.submit_to_cloud:
        command = f"""uv run python -m machineconfig.cluster.templates.cli_click --file {choice_file} """
        if args.function is not None:
            command += f"--function {args.function} "

    if args.optimized:
        command = command.replace("python ", "python -OO ")

    if args.zellij_tab is not None:
        comman_path__ = Path.home().joinpath(f"tmp_results/tmp_scripts/zellij_commands/{choice_file.stem}_{randstr_func(10)}.sh")
        comman_path__.parent.mkdir(parents=True, exist_ok=True)
        comman_path__.write_text(command, encoding="utf-8")
        console.print(Panel(Syntax(command, lexer="shell"), title=f"🔥 fire command @ {comman_path__}: "), style="bold red")
        import subprocess

        existing_tab_names = subprocess.run(["zellij", "action", "query-tab-names"], capture_output=True, text=True, check=True).stdout.splitlines()
        if args.zellij_tab in existing_tab_names:
            print(f"⚠️ Tab name `{args.zellij_tab}` already exists. Please choose a different name.")
            args.zellij_tab += f"_{randstr_func(3)}"
        from machineconfig.cluster.sessions_managers.zellij_local import run_command_in_zellij_tab

        command = run_command_in_zellij_tab(command=str(comman_path__), tab_name=args.zellij_tab, cwd=None)

    if args.watch:
        command = "watchexec --restart --exts py,sh,ps1 " + command

    if args.git_pull:
        command = f"\ngit -C {choice_file.parent} pull\n" + command

    if args.PathExport:
        from machineconfig.scripts.python.helpers.helpers_fire_command.file_wrangler import add_to_path
        export_line = add_to_path(path_variable="PYTHONPATH", directory=str(repo_root))
        command = export_line + "\n" + command

    if args.loop:
        import platform
        if platform.system() in ["Linux", "Darwin"]:
            command = command + "\nsleep 0.5"
        elif platform.system() == "Windows":
            command = "$ErrorActionPreference = 'SilentlyContinue';\n" + command + "\nStart-Sleep -Seconds 0.5"
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported.")

    return command
