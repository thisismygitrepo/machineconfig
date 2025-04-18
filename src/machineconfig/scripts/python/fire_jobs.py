"""
fire

# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for display_options build TUI
# https://github.com/chriskiehl/Gooey build commandline interface

"""


from machineconfig.scripts.python.helpers.helpers4 import search_for_files_of_interest
from machineconfig.scripts.python.helpers.helpers4 import convert_kwargs_to_fire_kwargs_str
from machineconfig.scripts.python.helpers.helpers4 import parse_pyfile
from machineconfig.scripts.python.helpers.helpers4 import get_import_module_code
from machineconfig.utils.utils import display_options, choose_one_option, PROGRAM_PATH, match_file_name, sanitize_path
from machineconfig.utils.ve_utils.ve1 import get_ve_activate_line, get_ve_name_and_ipython_profile
from crocodile.file_management import P, Read
from crocodile.core import randstr
import platform
from typing import Optional
import argparse

from machineconfig.utils.ve_utils.ve1 import get_repo_root


str2obj = {"True": True, "False": False, "None": None}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path",     nargs='?', type=str, help="The directory containing the jobs", default=".")
    parser.add_argument("function", nargs='?', type=str, help="Fuction to run", default=None)
    # parser.add_argument("--function", "-f", type=str, help="The function to run", default="")
    parser.add_argument("--ve",              "-v", type=str, help="virtual enviroment name", default="")
    parser.add_argument("--cmd",             "-B", action="store_true", help="Create a cmd fire command to launch the the job asynchronously.")
    parser.add_argument("--interactive",     "-i", action="store_true", help="Whether to run the job interactively using IPython")
    parser.add_argument("--debug",           "-d", action="store_true", help="debug")
    parser.add_argument("--choose_function", "-c", action="store_true", help="debug")
    parser.add_argument("--loop",            "-l", action="store_true", help="infinite recusion (runs again after completion)")
    parser.add_argument("--jupyter",         "-j", action="store_true", help="open in a jupyter notebook")
    parser.add_argument("--submit_to_cloud", "-C", action="store_true", help="submit to cloud compute")
    parser.add_argument("--remote",          "-r", action="store_true", help="launch on a remote machine")
    parser.add_argument("--module",          "-m", action="store_true", help="launch the main file")
    parser.add_argument("--streamlit",       "-S", action="store_true", help="run as streamlit app")
    parser.add_argument("--holdDirectory",   "-D", action="store_true", help="hold current directory and avoid cd'ing to the script directory")
    parser.add_argument("--git_pull",        "-g", action="store_true", help="Start by pulling the git repo")
    parser.add_argument("--optimized", "-O", action="store_true", help="Run the optimized version of the function")
    parser.add_argument("--Nprocess",        "-p", type=int, help="Number of processes to use", default=1)
    parser.add_argument("--kw", nargs="*", default=None, help="keyword arguments to pass to the function in the form of k1 v1 k2 v2 ... (meaning k1=v1, k2=v2, etc)")
    parser.add_argument("--zellij_tab",      "-z", type=str, dest="zellij_tab", help="open in a new zellij tab")
    args = parser.parse_args()

    path_obj = sanitize_path(P(args.path))
    if not path_obj.exists():
        path_obj = match_file_name(sub_string=args.path)
    else: pass

    if path_obj.is_dir():
        print(f"🔍 Searching recursively for Python, PowerShell and Shell scripts in directory `{path_obj}`")
        files = search_for_files_of_interest(path_obj)
        choice_file = choose_one_option(options=files, fzf=True)
        choice_file = P(choice_file)
    else:
        choice_file = path_obj
    print(f"💾 Selected file: {choice_file}")

    ve_name_suggested, ipy_profile = get_ve_name_and_ipython_profile(choice_file)
    if ipy_profile is None: ipy_profile = "default"
    activate_ve_line  = get_ve_activate_line(ve_name=args.ve or ve_name_suggested, a_path=str(choice_file))

    # Convert args.kw to dictionary
    if choice_file.suffix == ".py":
        if args.kw is not None:
            assert len(args.kw) % 2 == 0, f"args.kw must be a list of even length. Got {len(args.kw)}"
            kwargs = dict(zip(args.kw[::2], args.kw[1::2]))
            for key, value in kwargs.items():
                if value in str2obj:
                    kwargs[key] = str2obj[value]
            if args.function is None:  # if user passed arguments and forgot to pass function, then assume they want to run the main function.
                args.choose_function = True
        else:
            kwargs = {}
    else:
        kwargs = {}

    # =========================  choosing function to run
    if args.choose_function or args.submit_to_cloud:
        if choice_file.suffix == ".py":
            options, func_args = parse_pyfile(file_path=str(choice_file))
            choice_function_tmp = display_options(msg="Choose a function to run", options=options, fzf=True, multi=False)
            assert isinstance(choice_function_tmp, str), f"choice_function must be a string. Got {type(choice_function_tmp)}"
            choice_index = options.index(choice_function_tmp)
            choice_function: Optional[str] = choice_function_tmp.split(' -- ')[0]
            choice_function_args = func_args[choice_index]

            if choice_function == "RUN AS MAIN": choice_function = None
            if len(choice_function_args) > 0 and len(kwargs) == 0:
                for item in choice_function_args:
                    kwargs[item.name] = input(f"Please enter a value for argument `{item.name}` (type = {item.type}) (default = {item.default}) : ") or item.default
        elif choice_file.suffix == ".sh":  # in this case, we choos lines.
            options = []
            for line in choice_file.read_text().splitlines():
                if line.startswith("#"): continue
                if line == "": continue
                if line.startswith("echo"): continue
                options.append(line)
            choice_line = choose_one_option(options=options, fzf=True)
            choice_file = P.tmpfile(suffix=".sh").write_text(choice_line)
            choice_function = None
    else:
        choice_function = args.function

    if choice_file.suffix == ".py":
        if args.streamlit:
            from crocodile.environment import get_network_addresses
            local_ip_v4 = get_network_addresses()["local_ip_v4"]
            computer_name = platform.node()
            port = 8501
            toml_path: Optional[P] = None
            toml_path_maybe = choice_file.parent.joinpath(".streamlit/config.toml")
            if toml_path_maybe.exists(): toml_path = toml_path_maybe
            elif choice_file.parent.name == "pages":
                toml_path_maybe = choice_file.parent.parent.joinpath(".streamlit/config.toml")
                if toml_path_maybe.exists(): toml_path = toml_path_maybe
            if toml_path is not None:
                config = Read.toml(toml_path)
                if "server" in config:
                    if "port" in config["server"]:
                        port = config["server"]["port"]
            message = f"🚀 Streamlit app is running @:\n1- http://{local_ip_v4}:{port}\n2- http://{computer_name}:{port}\n3- http://localhost:{port}"
            from rich.panel import Panel
            from rich import print as rprint
            rprint(Panel(message))
            exe = "streamlit run --server.address 0.0.0.0 --server.headless true"
            # exe = f"cd '{choice_file.parent}'; " + exe
        elif args.interactive is False: exe = "python"
        elif args.jupyter: exe = "jupyter-lab"
        else:            
            exe = f"ipython -i --no-banner --profile {ipy_profile} "
    elif choice_file.suffix == ".ps1" or choice_file.suffix == ".sh":
        exe = "."
    elif choice_file.suffix == "":
        exe = ""
    else:
        raise NotImplementedError(f"File type {choice_file.suffix} not supported, in the sense that I don't know how to fire it.")

    if args.module or (args.debug and args.choose_function):  # because debugging tools do not support choosing functions and don't interplay with fire module. So the only way to have debugging and choose function options is to import the file as a module into a new script and run the function of interest there and debug the new script.
        assert choice_file.suffix == ".py", f"File must be a python file to be imported as a module. Got {choice_file.suffix}"
        import_line = get_import_module_code(str(choice_file))
        repo_root = get_repo_root(str(choice_file))
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
    sys.path.append(r'{P(choice_file).parent}')
    {repo_root_add}
    from {P(choice_file).stem} import *
    print(fr"✅ Successfully imported `{choice_file}`")
"""
        if choice_function is not None:
            txt = txt + f"""
res = {choice_function}({('**' + str(kwargs)) if kwargs else ''})
"""

        txt = f"""
try:
    from rich.panel import Panel
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console()
    console.print(Panel(Syntax(code=r'''{txt}''', lexer='python'), title='Import Script'), style="bold red")
except ImportError as _ex:
    print(r'''{txt}''')
""" + txt
        choice_file = P.tmp().joinpath(f'tmp_scripts/python/{P(choice_file).parent.name}_{P(choice_file).stem}_{randstr()}.py').create(parents_only=True).write_text(txt)

    # =========================  determining basic command structure: putting together exe & choice_file & choice_function & pdb
    if args.debug:
        if platform.system() == "Windows":
            command = f"{exe} -m ipdb {choice_file} "  # pudb is not available on windows machines, use poor man's debugger instead.
        elif platform.system() in ["Linux", "Darwin"]:
            command = f"{exe} -m pudb {choice_file} "  # TODO: functions not supported yet in debug mode.
        else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
    elif args.module:
        # both selected function and kwargs are mentioned in the made up script, therefore no need for fire module.
        command = f"{exe} {choice_file} "
    elif choice_function is not None:
        kwargs_str = convert_kwargs_to_fire_kwargs_str(kwargs)
        command = f"{exe} -m fire {choice_file} {choice_function} {kwargs_str}"
    elif args.streamlit:
        # for .streamlit config to work, it needs to be in the current directory.
        if args.holdDirectory:
            command = f"{exe} {choice_file}"
        else:
            command = f"cd {choice_file.parent}\n\n{exe} {choice_file.name}\n\ncd {P.cwd()}"

    elif args.cmd:
        command = rf""" cd /d {choice_file.parent} & {exe} {choice_file.name} """
    else:
        if choice_file.suffix == "":
            kwargs_raw = " ".join(args.kw) if args.kw is not None else ""
            command = f"{exe} {choice_file} {kwargs_raw}"
        else:
            # command = f"cd {choice_file.parent}\n\n{exe} {choice_file.name}\n\ncd {P.cwd()}"
            command = f"{exe} {choice_file} "
    # this installs in ve env, which is not execution env
    # if "ipdb" in command: install_n_import("ipdb")
    # if "pudb" in command: install_n_import("pudb")

    if not args.cmd:
        if "ipdb" in command: command = f"pip install ipdb\n\n{command}"
        if "pudb" in command: command = f"pip install pudb\n\n{command}"
        command = f"{activate_ve_line}\n\n{command}"
    else:
        # CMD equivalent
        if "ipdb" in command: command = f"pip install ipdb & {command}"
        if "pudb" in command: command = f"pip install pudb & {command}"
        command = fr"""start cmd -Argument "/k %USERPROFILE%\venvs\{args.ve}\Scripts\activate.bat & {command} " """  # this works from powershell
        # this works from cmd  # command = fr""" start cmd /k "%USERPROFILE%\venvs\{args.ve}\Scripts\activate.bat & {command} " """ # because start in cmd is different from start in powershell (in powershell it is short for Start-Process)

    if args.submit_to_cloud:
        command = f"""
{activate_ve_line}
python -m machineconfig.cluster.templates.cli_click --file {choice_file} """
        if choice_function is not None:
            command += f"--function {choice_function} "

    # try: install_n_import("clipboard").copy(command)
    # except Exception as ex: print(f"Failed to copy command to clipboard. {ex}")

    if args.loop:
        command = command + "\n" + f". {PROGRAM_PATH}"

    if args.Nprocess > 1:
        lines = [f""" zellij action new-tab --name nProcess{randstr(2)}"""]
        command = command.replace(". activate_ve", ". $HOME/scripts/activate_ve")
        for an_arg in range(args.Nprocess):
            sub_command = f"{command} --idx={an_arg} --idx_max={args.Nprocess}"
            if args.optimized:
                sub_command = sub_command.replace("python ", "python -OO ")
            sub_command_path = P.tmpfile(suffix=".sh").write_text(sub_command)
            lines.append(f"""zellij action new-pane -- bash {sub_command_path}  """)
            lines.append("sleep 5")  # python tends to freeze if you launch instances within 1 microsecond of each other
        command = "\n".join(lines)

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
        comman_path__ = P.tmpfile(suffix=".sh").write_text(command)
        console.print(Panel(Syntax(command, lexer="shell"), title=f"🔥 fire command @ {comman_path__}: "), style="bold red")
        import subprocess
        existing_tab_names = subprocess.run(["zellij", "action", "query-tab-names"], capture_output=True, text=True, check=True).stdout.splitlines()
        if args.zellij_tab in existing_tab_names:
            print(f"⚠️ Tab name `{args.zellij_tab}` already exists. Please choose a different name.")
            # args.zellij_tab = input("Please enter a new tab name: ")
            args.zellij_tab += f"_{randstr(3)}"
        command = f"""
echo "Sleep 1 seconds to allow zellij to create a new tab"
sleep 1
zellij action new-tab --name {args.zellij_tab}
echo "Sleep 2 seconds to allow zellij to go to the new tab"
sleep 2
zellij action go-to-tab-name {args.zellij_tab}
echo "Sleep 2 seconds to allow zellij to start the new pane"
sleep 2
zellij action new-pane --direction down -- /bin/bash {comman_path__}
echo "Sleep 2 seconds to allow zellij to start the new pane"
sleep 1
zellij action move-focus up; sleep 2
echo "Sleep 2 seconds to allow zellij to close the pane"
sleep 1
zellij action close-pane; sleep 2
"""
    if args.git_pull:
        command = f"\ngit -C {choice_file.parent} pull\n\n" + command
    console.print(Panel(Syntax(command, lexer="shell"), title=f"🔥 fire command @ {PROGRAM_PATH}: "), style="bold red")
    PROGRAM_PATH.write_text(command)


if __name__ == '__main__':
    # options, func_args = parse_pyfile(file_path="C:/Users/aalsaf01/code/crocodile/myresources/crocodile/core.py")
    main()
