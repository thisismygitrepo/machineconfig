"""
fire

# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for choose_from_options build TUI
# https://github.com/chriskiehl/Gooey build commandline interface

"""

from typing import Optional, Annotated
import typer


def route(args: "FireJobArgs", fire_args: str = "") -> None:
    from pathlib import Path
    from machineconfig.utils.path_helper import get_choice_file
    from machineconfig.utils.accessories import get_repo_root, randstr
    choice_file = get_choice_file(args.path, suffixes=None)
    repo_root = get_repo_root(choice_file)
    print(f"💾 Selected file: {choice_file}.\nRepo root: {repo_root}")
    if args.marimo:
        print(f"🧽 Preparing to launch Marimo notebook for `{choice_file}`...")
        tmp_dir = Path.home().joinpath(f"tmp_results/tmp_scripts/marimo/{choice_file.stem}_{randstr()}")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        script = f"""
cd {tmp_dir}
uv run --python 3.14 --with marimo marimo convert {choice_file} -o marimo_nb.py
uv run --project {repo_root} --with marimo marimo edit --host 0.0.0.0 marimo_nb.py
"""
        from machineconfig.utils.code import exit_then_run_shell_script
        print(f"🚀 Launching Marimo notebook for `{choice_file}`...")
        exit_then_run_shell_script(script)
        return

    # =========================  preparing kwargs_dict
    if choice_file.suffix == ".py":
        from machineconfig.scripts.python.helpers_fire_command.fire_jobs_args_helper import extract_kwargs
        kwargs_dict = extract_kwargs(args)  # This now returns empty dict, but kept for compatibility
    else:
        kwargs_dict = {}

    # =========================  choosing function to run
    choice_function: Optional[str] = None  # Initialize to avoid unbound variable
    if args.choose_function:
        from machineconfig.scripts.python.helpers_fire_command.fire_jobs_route_helper import choose_function_or_lines

        choice_function, choice_file, kwargs_dict = choose_function_or_lines(choice_file, kwargs_dict)
    else:
        choice_function = args.function

    if choice_file.suffix == ".py":
        with_project = f"--project {repo_root} " if repo_root is not None else ""
        if args.streamlit:
            from machineconfig.scripts.python.helpers_fire_command.fire_jobs_route_helper import get_command_streamlit
            exe = get_command_streamlit(choice_file=choice_file, environment=args.environment, repo_root=repo_root)
            exe = f"uv run {with_project} {exe} "
        elif args.jupyter:
            exe = f"uv run {with_project} jupyter-lab"
        else:
            if args.interactive:
                from machineconfig.utils.ve import get_ve_path_and_ipython_profile
                _ve_root_from_file, ipy_profile = get_ve_path_and_ipython_profile(init_path=choice_file)
                if ipy_profile is None:
                    ipy_profile = "default"
                exe = f"uv run {with_project} ipython -i --no-banner --profile {ipy_profile} "
            else:
                exe = f"uv run {with_project} python "
    elif choice_file.suffix == ".ps1" or choice_file.suffix == ".sh":
        exe = "."
    elif choice_file.suffix == "":
        exe = ""
    else:
        raise NotImplementedError(f"File type {choice_file.suffix} not supported, in the sense that I don't know how to fire it.")

    if args.module or (args.debug and args.choose_function):
        # because debugging tools do not support choosing functions and don't interplay with fire module. So the only way to have debugging and choose function options is to import the file as a module into a new script and run the function of interest there and debug the new script.
        assert choice_file.suffix == ".py", f"File must be a python file to be imported as a module. Got {choice_file}"
        from machineconfig.scripts.python.helpers_fire_command.file_wrangler import get_import_module_code, wrap_import_in_try_except
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
        # print(f"🧩 Preparing import code for module import:\n{import_code}")
        code_printing = lambda_to_python_script(
            lambda: print_code(code=import_code_robust, lexer="python", desc="import as module code"),
            in_global=True, import_module=False
        )
        print(f"🧩 Preparing import code for module import:\n{import_code}")
        if choice_function is not None:
            calling = f"""res = {choice_function}({("**" + str(kwargs_dict)) if kwargs_dict else ""})"""
        else:
            calling = """# No function selected to call. You can add your code here."""
        choice_file = Path.home().joinpath(f"tmp_results/tmp_scripts/python/{Path(choice_file).parent.name}_{Path(choice_file).stem}_{randstr()}.py")
        choice_file.parent.mkdir(parents=True, exist_ok=True)
        choice_file.write_text(import_code_robust + "\n" + code_printing + "\n" + calling, encoding="utf-8")

    # =========================  determining basic command structure: putting together exe & choice_file & choice_function & pdb
    if args.debug:
        import platform
        if platform.system() == "Windows":
            command = f"{exe} -m ipdb {choice_file} "  # pudb is not available on windows machines, use poor man's debugger instead.
        elif platform.system() in ["Linux", "Darwin"]:
            command = f"{exe} -m pudb {choice_file} "  # TODO: functions not supported yet in debug mode.
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported.")
    elif args.module:
        # both selected function and kwargs are mentioned in the made up script, therefore no need for fire module.
        command = f"{exe} {choice_file} "
    elif choice_function is not None and choice_file.suffix == ".py":
        command = f"{exe} -m fire {choice_file} {choice_function} {fire_args}"
    elif args.streamlit:
        # for .streamlit config to work, it needs to be in the current directory.
        if args.holdDirectory:
            command = f"{exe} {choice_file}"
        else:
            command = f"cd {choice_file.parent}\n{exe} {choice_file.name}\ncd {Path.cwd()}"
    elif args.cmd:
        command = rf""" cd /d {choice_file.parent} & {exe} {choice_file.name} """
    else:
        if choice_file.suffix == "":
            command = f"{exe} {choice_file} {fire_args}"
        else:
            command = f"{exe} {choice_file} "

    if not args.cmd:
        pass
    else:
        new_line = "\n"
        command = rf"""start cmd -Argument "/k {command.replace(new_line, " & ")} " """  # this works from powershell
    if args.submit_to_cloud:
        command = f"""uv run python -m machineconfig.cluster.templates.cli_click --file {choice_file} """
        if choice_function is not None:
            command += f"--function {choice_function} "

    if args.optimized:
        command = command.replace("python ", "python -OO ")

    from rich.panel import Panel
    from rich.console import Console
    from rich.syntax import Syntax

    console = Console()
    if args.zellij_tab is not None:
        comman_path__ = Path.home().joinpath(f"tmp_results/tmp_scripts/zellij_commands/{choice_file.stem}_{randstr()}.sh")
        comman_path__.parent.mkdir(parents=True, exist_ok=True)
        comman_path__.write_text(command, encoding="utf-8")
        console.print(Panel(Syntax(command, lexer="shell"), title=f"🔥 fire command @ {comman_path__}: "), style="bold red")
        import subprocess

        existing_tab_names = subprocess.run(["zellij", "action", "query-tab-names"], capture_output=True, text=True, check=True).stdout.splitlines()
        if args.zellij_tab in existing_tab_names:
            print(f"⚠️ Tab name `{args.zellij_tab}` already exists. Please choose a different name.")
            args.zellij_tab += f"_{randstr(3)}"
        from machineconfig.cluster.sessions_managers.zellij_local import run_command_in_zellij_tab

        command = run_command_in_zellij_tab(command=str(comman_path__), tab_name=args.zellij_tab, cwd=None)
    if args.watch:
        command = "watchexec --restart --exts py,sh,ps1 " + command
    if args.git_pull:
        command = f"\ngit -C {choice_file.parent} pull\n" + command
    if args.PathExport:
        from machineconfig.scripts.python.helpers_fire_command.file_wrangler import add_to_path

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
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=command, strict=False)


def fire(
    ctx: typer.Context,
    path: Annotated[str, typer.Argument(help="Path to the Python file to run")] = ".",
    function: Annotated[Optional[str], typer.Argument(help="Function to run")] = None,
    ve: Annotated[str, typer.Option("--ve", "-v", help="Virtual environment name")] = "",
    cmd: Annotated[bool, typer.Option("--cmd", "-B", help="Create a cmd fire command to launch the job asynchronously")] = False,
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Whether to run the job interactively using IPython")] = False,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Enable debug mode")] = False,
    choose_function: Annotated[bool, typer.Option("--choose-function", "-c", help="Choose function interactively")] = False,
    loop: Annotated[bool, typer.Option("--loop", "-l", help="Infinite recursion (runs again after completion/interruption)")] = False,
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="Open in a jupyter notebook")] = False,
    marimo: Annotated[bool, typer.Option("--marimo", "-M", help="Open in a marimo notebook")] = False,
    module: Annotated[bool, typer.Option("--module", "-m", help="Launch the main file")] = False,
    optimized: Annotated[bool, typer.Option("--optimized", "-O", help="Run the optimized version of the function")] = False,
    zellij_tab: Annotated[Optional[str], typer.Option("--zellij-tab", "-z", help="Open in a new zellij tab")] = None,
    submit_to_cloud: Annotated[bool, typer.Option("--submit-to-cloud", "-C", help="Submit to cloud compute")] = False,
    remote: Annotated[bool, typer.Option("--remote", "-r", help="Launch on a remote machine")] = False,
    streamlit: Annotated[bool, typer.Option("--streamlit", "-S", help="Run as streamlit app")] = False,
    environment: Annotated[str, typer.Option("--environment", "-E", help="Choose ip, localhost, hostname or arbitrary url")] = "",
    holdDirectory: Annotated[
        bool, typer.Option("--holdDirectory", "-D", help="Hold current directory and avoid cd'ing to the script directory")
    ] = False,
    PathExport: Annotated[bool, typer.Option("--PathExport", "-P", help="Augment the PYTHONPATH with repo root")] = False,
    git_pull: Annotated[bool, typer.Option("--git-pull", "-g", help="Start by pulling the git repo")] = False,
    watch: Annotated[bool, typer.Option("--watch", "-w", help="Watch the file for changes")] = False,
) -> None:
    """Main function to process fire jobs arguments."""

    # Get Fire arguments from context
    from machineconfig.scripts.python.helpers_fire_command.fire_jobs_args_helper import FireJobArgs, parse_fire_args_from_context
    fire_args = parse_fire_args_from_context(ctx)

    args = FireJobArgs(
        path=path,
        function=function,
        ve=ve,
        cmd=cmd,
        interactive=interactive,
        debug=debug,
        choose_function=choose_function,
        loop=loop,
        jupyter=jupyter,
        marimo=marimo,
        submit_to_cloud=submit_to_cloud,
        remote=remote,
        module=module,
        streamlit=streamlit,
        environment=environment,
        holdDirectory=holdDirectory,
        PathExport=PathExport,
        git_pull=git_pull,
        optimized=optimized,
        zellij_tab=zellij_tab,
        watch=watch,
    )
    try:
        route(args, fire_args)
    except SystemExit:
        # Re-raise SystemExit to preserve exit codes and allow clean exits
        raise
    except Exception as e:
        # For other exceptions, print clean error message and exit
        import sys

        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def get_app():
    from typer import Typer

    app = Typer(add_completion=False)
    app.command(context_settings={"allow_extra_args": True, "allow_interspersed_args": False})(fire)
    return app


def main():
    app = get_app()
    app()


if __name__ == "__main__":
    from machineconfig.scripts.python.helpers_fire_command.fire_jobs_args_helper import FireJobArgs
