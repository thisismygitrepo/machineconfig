"""
fire

# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for choose_from_options build TUI
# https://github.com/chriskiehl/Gooey build commandline interface

"""

from machineconfig.scripts.python.helpers.helpers4 import search_for_files_of_interest
from machineconfig.scripts.python.helpers.helpers4 import parse_pyfile
from machineconfig.scripts.python.helpers.helpers4 import get_import_module_code
from machineconfig.utils.ve import get_ve_activate_line, get_ve_path_and_ipython_profile
from machineconfig.utils.options import choose_from_options
from machineconfig.utils.path_helper import match_file_name, sanitize_path

from machineconfig.utils.path_extended import PathExtended as PathExtended
from machineconfig.utils.accessories import get_repo_root, randstr
from machineconfig.scripts.python.fire_jobs_args_helper import FireJobArgs, extract_kwargs, parse_fire_args_from_context
import platform
from typing import Optional, Annotated
from pathlib import Path
import tomllib
import typer
# import os


def route(args: FireJobArgs, fire_args: str = "") -> None:
    if args.layout:
        from machineconfig.scripts.python.fire_jobs_layout_helper import handle_layout_args

        return handle_layout_args(args)

    path_obj = sanitize_path(args.path)
    if not path_obj.exists():
        suffixes = {".py", ".sh", ".ps1"}
        choice_file = match_file_name(sub_string=args.path, search_root=PathExtended.cwd(), suffixes=suffixes)
    elif path_obj.is_dir():
        print(f"🔍 Searching recursively for Python, PowerShell and Shell scripts in directory `{path_obj}`")
        files = search_for_files_of_interest(path_obj)
        print(f"🔍 Got #{len(files)} results.")
        choice_file = choose_from_options(multi=False, options=files, fzf=True, msg="Choose one option")
        choice_file = PathExtended(choice_file)
    else:
        choice_file = path_obj
    repo_root = get_repo_root(Path(choice_file))
    print(f"💾 Selected file: {choice_file}.\nRepo root: {repo_root}")
    ve_root_from_file, ipy_profile = get_ve_path_and_ipython_profile(choice_file)
    if ipy_profile is None:
        ipy_profile = "default"

    if choice_file.suffix == ".py":
        kwargs = extract_kwargs(args)  # This now returns empty dict, but kept for compatibility
        activate_ve_line = get_ve_activate_line(ve_root=args.ve or ve_root_from_file or "$HOME/code/machineconfig/.venv")
    else:
        activate_ve_line = ""
        kwargs = {}

    # =========================  choosing function to run
    choice_function: Optional[str] = None  # Initialize to avoid unbound variable
    if args.choose_function or args.submit_to_cloud:
        if choice_file.suffix == ".py":
            options, func_args = parse_pyfile(file_path=str(choice_file))
            choice_function_tmp = choose_from_options(msg="Choose a function to run", options=options, fzf=True, multi=False)
            assert isinstance(choice_function_tmp, str), f"choice_function must be a string. Got {type(choice_function_tmp)}"
            choice_index = options.index(choice_function_tmp)
            choice_function = choice_function_tmp.split(" -- ")[0]
            choice_function_args = func_args[choice_index]

            if choice_function == "RUN AS MAIN":
                choice_function = None
            if len(choice_function_args) > 0 and len(kwargs) == 0:
                for item in choice_function_args:
                    kwargs[item.name] = input(f"Please enter a value for argument `{item.name}` (type = {item.type}) (default = {item.default}) : ") or item.default
        elif choice_file.suffix == ".sh":  # in this case, we choos lines.
            options = []
            for line in choice_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("#"):
                    continue
                if line == "":
                    continue
                if line.startswith("echo"):
                    continue
                options.append(line)
            chosen_lines = choose_from_options(msg="Choose a line to run", options=options, fzf=True, multi=True)
            choice_file = PathExtended.tmpfile(suffix=".sh")
            choice_file.parent.mkdir(parents=True, exist_ok=True)
            choice_file.write_text("\n".join(chosen_lines), encoding="utf-8")
            choice_function = None
    else:
        choice_function = args.function

    if choice_file.suffix == ".py":
        if args.streamlit:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 1))
                local_ip_v4 = s.getsockname()[0]
            except Exception:
                local_ip_v4 = socket.gethostbyname(socket.gethostname())
            finally:
                s.close()
            computer_name = platform.node()
            port = 8501
            toml_path: Optional[PathExtended] = None
            toml_path_maybe = choice_file.parent.joinpath(".streamlit/config.toml")
            if toml_path_maybe.exists():
                toml_path = toml_path_maybe
            elif choice_file.parent.name == "pages":
                toml_path_maybe = choice_file.parent.parent.joinpath(".streamlit/config.toml")
                if toml_path_maybe.exists():
                    toml_path = toml_path_maybe
            if toml_path is not None:
                print(f"📄 Reading config.toml @ {toml_path}")
                config = tomllib.loads(toml_path.read_text(encoding="utf-8"))
                if "server" in config:
                    if "port" in config["server"]:
                        port = config["server"]["port"]
                secrets_path = toml_path.with_name("secrets.toml")
                if repo_root is not None:
                    secrets_template_path = PathExtended.home().joinpath(f"dotfiles/creds/streamlit/{PathExtended(repo_root).name}/{choice_file.name}/secrets.toml")
                    if args.environment != "" and not secrets_path.exists() and secrets_template_path.exists():
                        secrets_template = tomllib.loads(secrets_template_path.read_text(encoding="utf-8"))
                        if args.environment == "ip":
                            host_url = f"http://{local_ip_v4}:{port}/oauth2callback"
                        elif args.environment == "localhost":
                            host_url = f"http://localhost:{port}/oauth2callback"
                        elif args.environment == "hostname":
                            host_url = f"http://{computer_name}:{port}/oauth2callback"
                        else:
                            host_url = f"http://{args.environment}:{port}/oauth2callback"
                        try:
                            secrets_template["auth"]["redirect_uri"] = host_url
                            secrets_template["auth"]["cookie_secret"] = randstr(35)
                            secrets_template["auth"]["auth0"]["redirect_uri"] = host_url
                            # save_toml(obj=secrets_template, path=secrets_path)
                        except Exception as ex:
                            print(ex)
                            raise ex
            message = f"🚀 Streamlit app is running @:\n1- http://{local_ip_v4}:{port}\n2- http://{computer_name}:{port}\n3- http://localhost:{port}"
            from rich.panel import Panel
            from rich import print as rprint

            rprint(Panel(message))
            exe = f"streamlit run --server.address 0.0.0.0 --server.headless true --server.port {port}"
            # exe = f"cd '{choice_file.parent}'; " + exe
        elif args.interactive is False:
            exe = "python"
        elif args.jupyter:
            exe = "jupyter-lab"
        else:
            exe = f"ipython -i --no-banner --profile {ipy_profile} "
    elif choice_file.suffix == ".ps1" or choice_file.suffix == ".sh":
        exe = "."
    elif choice_file.suffix == "":
        exe = ""
    else:
        raise NotImplementedError(f"File type {choice_file.suffix} not supported, in the sense that I don't know how to fire it.")

    if (
        args.module or (args.debug and args.choose_function)
    ):  # because debugging tools do not support choosing functions and don't interplay with fire module. So the only way to have debugging and choose function options is to import the file as a module into a new script and run the function of interest there and debug the new script.
        assert choice_file.suffix == ".py", f"File must be a python file to be imported as a module. Got {choice_file}"
        import_line = get_import_module_code(str(choice_file))
        if repo_root is not None:
            repo_root_add = f"""sys.path.append(r'{repo_root}')"""
        else:
            repo_root_add = ""
        txt: str = f"""
try:
    {import_line}
except (ImportError, ModuleNotFoundError) as ex:
    print(fr"❌ Failed to import `{choice_file}` as a module: {{ex}} ")
    print(fr"⚠️ Attempting import with ad-hoc `$PATH` manipulation. DO NOT pickle any objects in this session as correct deserialization cannot be guaranteed.")
    import sys
    sys.path.append(r'{PathExtended(choice_file).parent}')
    {repo_root_add}
    from {PathExtended(choice_file).stem} import *
    print(fr"✅ Successfully imported `{choice_file}`")
"""
        if choice_function is not None:
            txt = (
                txt
                + f"""
res = {choice_function}({("**" + str(kwargs)) if kwargs else ""})
"""
            )

        txt = (
            f"""
try:
    from rich.panel import Panel
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console()
    console.print(Panel(Syntax(code=r'''{txt}''', lexer='python'), title='Import Script'), style="bold red")
except ImportError as _ex:
    print(r'''{txt}''')
"""
            + txt
        )
        choice_file = PathExtended.tmp().joinpath(f"tmp_scripts/python/{PathExtended(choice_file).parent.name}_{PathExtended(choice_file).stem}_{randstr()}.py")
        choice_file.parent.mkdir(parents=True, exist_ok=True)
        choice_file.write_text(txt, encoding="utf-8")

    # =========================  determining basic command structure: putting together exe & choice_file & choice_function & pdb
    if args.debug:
        if platform.system() == "Windows":
            command = f"{exe} -m ipdb {choice_file} "  # pudb is not available on windows machines, use poor man's debugger instead.
        elif platform.system() in ["Linux", "Darwin"]:
            command = f"{exe} -m pudb {choice_file} "  # TODO: functions not supported yet in debug mode.
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported.")
    elif args.module:
        # both selected function and kwargs are mentioned in the made up script, therefore no need for fire module.
        command = f"{exe} {choice_file} "
    elif choice_function is not None:
        command = f"{exe} -m fire {choice_file} {choice_function} {fire_args}"
    elif args.streamlit:
        # for .streamlit config to work, it needs to be in the current directory.
        if args.holdDirectory:
            command = f"{exe} {choice_file}"
        else:
            command = f"cd {choice_file.parent}\n{exe} {choice_file.name}\ncd {PathExtended.cwd()}"

    elif args.cmd:
        command = rf""" cd /d {choice_file.parent} & {exe} {choice_file.name} """
    else:
        if choice_file.suffix == "":
            command = f"{exe} {choice_file} {fire_args}"
        else:
            # command = f"cd {choice_file.parent}\n{exe} {choice_file.name}\ncd {PathExtended.cwd()}"
            command = f"{exe} {choice_file} "
    if not args.cmd:
        if "ipdb" in command:
            command = f"pip install ipdb\n{command}"
        if "pudb" in command:
            command = f"pip install pudb\n{command}"
        command = f"{activate_ve_line}\n{command}"
    else:
        # CMD equivalent
        if "ipdb" in command:
            command = f"pip install ipdb & {command}"
        if "pudb" in command:
            command = f"pip install pudb & {command}"
        new_line = "\n"
        command = rf"""start cmd -Argument "/k {activate_ve_line.replace(".ps1", ".bat").replace(". ", "")} & {command.replace(new_line, " & ")} " """  # this works from powershell

    if args.submit_to_cloud:
        command = f"""
{activate_ve_line}
python -m machineconfig.cluster.templates.cli_click --file {choice_file} """
        if choice_function is not None:
            command += f"--function {choice_function} "

    if args.Nprocess > 1:
        from machineconfig.cluster.sessions_managers.zellij_local import run_zellij_layout
        from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig

        layout: LayoutConfig = {"layoutName": "fireNprocess", "layoutTabs": []}
        for an_arg in range(args.Nprocess):
            layout["layoutTabs"].append({"tabName": f"tab{an_arg}", "startDir": str(PathExtended.cwd()), "command": f"uv run -m fire {choice_file} {choice_function} --idx={an_arg} --idx_max={args.Nprocess}"})
        run_zellij_layout(layout_config=layout)
        return None

    if args.optimized:
        # note that in ipython, optimization is meaningless.
        command = command.replace("python ", "python -OO ")
    # if platform.system() == "Linux":
    #     command = "timeout 1s aafire -driver slang\nclear\n" + command

    from rich.panel import Panel
    from rich.console import Console
    from rich.syntax import Syntax

    console = Console()

    if args.zellij_tab is not None:
        comman_path__ = PathExtended.tmpfile(suffix=".sh")
        comman_path__.parent.mkdir(parents=True, exist_ok=True)
        comman_path__.write_text(command, encoding="utf-8")
        console.print(Panel(Syntax(command, lexer="shell"), title=f"🔥 fire command @ {comman_path__}: "), style="bold red")
        import subprocess

        existing_tab_names = subprocess.run(["zellij", "action", "query-tab-names"], capture_output=True, text=True, check=True).stdout.splitlines()
        if args.zellij_tab in existing_tab_names:
            print(f"⚠️ Tab name `{args.zellij_tab}` already exists. Please choose a different name.")
            # args.zellij_tab = input("Please enter a new tab name: ")
            args.zellij_tab += f"_{randstr(3)}"
        from machineconfig.cluster.sessions_managers.zellij_local import run_command_in_zellij_tab

        command = run_command_in_zellij_tab(command=str(comman_path__), tab_name=args.zellij_tab, cwd=None)
    if args.watch:
        command = "watchexec --restart --exts py,sh,ps1 " + command
    if args.git_pull:
        command = f"\ngit -C {choice_file.parent} pull\n" + command
    if args.PathExport:
        if platform.system() in ["Linux", "Darwin"]:
            export_line = f"""export PYTHONPATH="{repo_root}""" + """:${PYTHONPATH}" """
        elif platform.system() == "Windows":
            # export_line = f"""set PYTHONPATH="{repo_root}""" + """:%PYTHONPATH%" """
            # powershell equivalent
            export_line = f"""$env:PYTHONPATH="{repo_root}""" + """:$env:PYTHONPATH" """
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported.")
        command = export_line + "\n" + command

    # program_path = os.environ.get("op_script", None)
    # program_path = PathExtended(program_path) if program_path is not None else PROGRAM_PATH
    if args.loop:
        if platform.system() in ["Linux", "Darwin"]:
            command = command + "\nsleep 0.5"
        elif platform.system() == "Windows":
            # command = command + "timeout 0.5\n"
            # pwsh equivalent
            command = "$ErrorActionPreference = 'SilentlyContinue';\n" + command + "\nStart-Sleep -Seconds 0.5"
        else:
            raise NotImplementedError(f"Platform {platform.system()} not supported.")
        # command = command + f"\n. {program_path}"
    console.print(Panel(Syntax(command, lexer="shell"), title=f"🔥 fire command @ {command}: "), style="bold red")
    # program_path.parent.mkdir(parents=True, exist_ok=True)
    # program_path.write_text(command, encoding="utf-8")
    import subprocess

    subprocess.run(command, shell=True, check=True)


def main(
    ctx: typer.Context,
    path: Annotated[str, typer.Argument(help="Path to the Python file to run")] = ".",
    function: Annotated[Optional[str], typer.Argument(help="Function to run")] = None,
    ve: Annotated[str, typer.Option("--ve", "-v", help="Virtual environment name")] = "",
    cmd: Annotated[bool, typer.Option("--cmd", "-B", help="Create a cmd fire command to launch the job asynchronously")] = False,
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Whether to run the job interactively using IPython")] = False,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Enable debug mode")] = False,
    choose_function: Annotated[bool, typer.Option("--choose_function", "-c", help="Choose function interactively")] = False,
    loop: Annotated[bool, typer.Option("--loop", "-l", help="Infinite recursion (runs again after completion/interruption)")] = False,
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="Open in a jupyter notebook")] = False,
    submit_to_cloud: Annotated[bool, typer.Option("--submit_to_cloud", "-C", help="Submit to cloud compute")] = False,
    remote: Annotated[bool, typer.Option("--remote", "-r", help="Launch on a remote machine")] = False,
    module: Annotated[bool, typer.Option("--module", "-m", help="Launch the main file")] = False,
    streamlit: Annotated[bool, typer.Option("--streamlit", "-S", help="Run as streamlit app")] = False,
    environment: Annotated[str, typer.Option("--environment", "-E", help="Choose ip, localhost, hostname or arbitrary url")] = "",
    holdDirectory: Annotated[bool, typer.Option("--holdDirectory", "-D", help="Hold current directory and avoid cd'ing to the script directory")] = False,
    PathExport: Annotated[bool, typer.Option("--PathExport", "-P", help="Augment the PYTHONPATH with repo root")] = False,
    git_pull: Annotated[bool, typer.Option("--git_pull", "-g", help="Start by pulling the git repo")] = False,
    optimized: Annotated[bool, typer.Option("--optimized", "-O", help="Run the optimized version of the function")] = False,
    Nprocess: Annotated[int, typer.Option("--Nprocess", "-p", help="Number of processes to use")] = 1,
    zellij_tab: Annotated[Optional[str], typer.Option("--zellij_tab", "-z", help="Open in a new zellij tab")] = None,
    watch: Annotated[bool, typer.Option("--watch", "-w", help="Watch the file for changes")] = False,
    layout: Annotated[bool, typer.Option("--layout", "-L", help="Use layout configuration (Zellij Or WindowsTerminal)")] = False,
) -> None:
    """Main function to process fire jobs arguments."""
    
    # Get Fire arguments from context
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
        submit_to_cloud=submit_to_cloud,
        remote=remote,
        module=module,
        streamlit=streamlit,
        environment=environment,
        holdDirectory=holdDirectory,
        PathExport=PathExport,
        git_pull=git_pull,
        optimized=optimized,
        Nprocess=Nprocess,
        zellij_tab=zellij_tab,
        watch=watch,
        layout=layout,
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


def main_from_parser():
    # from trogon.typer import init_tui
    # from trogon.typer import init_tui
    from typer import Typer
    app = Typer(add_completion=False)
    app.command(context_settings={"allow_extra_args": True, "allow_interspersed_args": False})(main)
    # typer.run(main)
    # init_tui(app)
    app()


if __name__ == "__main__":
    # options, func_args = parse_pyfile(file_path="C:/Users/aalsaf01/code/machineconfig/myresources/crocodile/core.py")
    main_from_parser()
