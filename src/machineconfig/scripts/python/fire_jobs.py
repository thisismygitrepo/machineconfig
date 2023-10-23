
"""
fire
"""

import crocodile.toolbox as tb
import platform
from machineconfig.utils.utils import display_options, PROGRAM_PATH, choose_ssh_host, match_file_name
# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for display_options build TUI
# https://github.com/chriskiehl/Gooey build commandline interface
import inspect
from typing import Callable, Any
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs='?', type=str, help="The directory containing the jobs", default=".")
    parser.add_argument("--function", "-f", type=str, help="The function to run", default="")
    parser.add_argument("--ve", "-v", type=str, help="virtual enviroment name", default="")
    parser.add_argument("--cmd", "-B", action="store_true", help="Create a cmd fire command to launch the the job asynchronously.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Whether to run the job interactively using IPython")
    parser.add_argument("--debug", "-d", action="store_true", help="debug")
    parser.add_argument("--choose_function", "-c", action="store_true", help="debug")
    parser.add_argument("--submit_to_cloud", "-C", action="store_true", help="submit to cloud compute")
    parser.add_argument("--remote", "-r", action="store_true", help="launch on a remote machine")
    parser.add_argument("--module", "-m", action="store_true", help="launch the main file")
    parser.add_argument("--streamlit", "-S", action="store_true", help="run as streamlit app")
    parser.add_argument("--history", "-H", action="store_true", help="choose from history")
    parser.add_argument("--kw", nargs="*", default=None, help="keyword arguments to pass to the function in the form of k1 v1 k2 v2 ...")

    args = parser.parse_args()
    if args.kw is not None:
        assert len(args.kw) % 2 == 0, f"args.kw must be a list of even length. Got {len(args.kw)}"
        kwargs = dict(zip(args.kw[::2], args.kw[1::2]))
        # print(f"kwargs = {kwargs}")
    else:
        kwargs = {}

    path_obj = tb.P(args.path).expanduser().absolute()
    if not path_obj.exists(): path_obj = match_file_name(args.path)

    if path_obj.is_dir():
        print(f"Seaching recursively for all python file in directory `{path_obj}`")
        py_files = path_obj.search(pattern="*.py", not_in=["__init__.py"], r=True).list
        choice_file = display_options(msg="Choose a file to run", options=py_files, fzf=True, multi=False)
        assert not isinstance(choice_file, list), f"choice_file must be a string. Got {type(choice_file)}"
        choice_file = tb.P(choice_file)
    else:
        choice_file = path_obj

    if args.choose_function or args.submit_to_cloud:
        # assert isinstance(choice_file, str), f"choice_file must be a string. Got {type(choice_file)}"
        _module, choice_function = choose_function(str(choice_file))
        if choice_function == "RUN AS MAIN": choice_function = None
        # if choice_function != "RUN AS MAIN":
            # kgs1, _ = interactively_run_function(module[choice_function])
            # " ".join([f"--{k} {v}" for k, v in kgs1.items()])
    elif args.function != "":
        choice_function = args.function
    else:
        choice_function = None

    if args.submit_to_cloud:
        submit_to_cloud(func=choice_function if choice_function is not None else choice_file)
        return

    if args.ve == "":
        from machineconfig.utils.ve import get_ve_profile  # if file name is passed explicitly, then, user probably launched it from cwd different to repo root, so activate_ve can't infer ve from .ve_path, so we attempt to do that manually here
        args.ve = get_ve_profile(choice_file)

    if args.streamlit: exe = "streamlit run"
    elif args.interactive is False: exe = "python"
    else:
        from machineconfig.utils.ve import get_ipython_profile
        exe = f"ipython -i --no-banner --profile {get_ipython_profile(choice_file)} "

    if args.module or (args.debug and args.choose_function):  # because debugging tools do not support choosing functions and don't interplay with fire module. So the only way to have debugging and choose function options is to import the file as a module into a new script and run the function of interest there and debug the new script.
        txt: str = f"""
import sys
sys.path.append(r'{tb.P(choice_file).parent}')
from {tb.P(choice_file).stem} import *
"""
        if choice_function is not None:
            txt = txt + f"""
{choice_function}({('**' + str(kwargs)) if kwargs else ''})
"""
        txt = f"""
from machineconfig.utils.utils import print_programming_script
print_programming_script(r'''{txt}''', lexer='python', desc='Imported Script')
""" + txt
        choice_file = tb.P.tmp().joinpath(f'tmp_scripts/python/{tb.P(choice_file).parent.name}_{tb.P(choice_file).stem}_{tb.randstr()}.py').create(parents_only=True).write_text(txt)

    # determining basic command structure: putting together exe & choice_file & choice_function & pdb
    if args.debug:
        if platform.system() == "Windows":
            command = f"{exe} -m ipdb {choice_file} "  # pudb is not available on windows machines, use poor man's debugger instead.
        elif platform.system() in ["Linux", "Darwin"]:
            command = f"{exe} -m pudb {choice_file} "  # TODO: functions not supported yet in debug mode.
        else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
    elif choice_function is not None:
        # https://google.github.io/python-fire/guide/
        tmp = f"'{kwargs}'" if kwargs else ''
        command = f"{exe} -m fire {choice_file} {choice_function} {tmp}"
    else:
        if not args.streamlit:
            command = f"{exe} {choice_file} "
        else:
            if not args.cmd:
                # for .streamlit config to work, it needs to be in the current directory.
                command = f"cd {choice_file.parent}; {exe} {choice_file.name}; cd {tb.P.cwd()}"
            else:
                command = rf""" cd /d {choice_file.parent} & {exe} {choice_file.name} """

    if "ipdb" in command: tb.install_n_import("ipdb")
    if "pudb" in command: tb.install_n_import("pudb")

    if not args.cmd:
        command = f". activate_ve {args.ve}; {command}"
    else:
        # this works from powershell
        command = fr"""start cmd -Argument "/k %USERPROFILE%\venvs\{args.ve}\Scripts\activate.bat & {command} " """
        # this works from cmd
        # command = fr""" start cmd /k "%USERPROFILE%\venvs\{args.ve}\Scripts\activate.bat & {command} " """
        # because start in cmd is different from start in powershell (in powershell it is short for Start-Process)

    # if args.remote: return run_on_remote(choice_file, args=args)
    try: tb.install_n_import("clipboard").copy(command)
    except Exception as ex: print(f"Failed to copy command to clipboard. {ex}")
    # TODO: send this command to terminal history. In powershell & bash there is no way to do it with a command other than goiing to history file. In Mcfly there is a way but its linux only tool.
    # if platform.system() == "Windows": command = f" ({command}) | Add-History  -PassThru "
    print(f"🔥 command:\n{command}\n\n")
    PROGRAM_PATH.write_text(command)


def choose_function(file_path: str):
    print(f"Loading {file_path} ...")
    module: tb.Struct = tb.P(file_path).readit()
    module = module.filter(lambda k, v: "function" in str(type(v)))
    module.print()
    options = module.apply(lambda k, v: f"{k} -- {type(v)} {tb.Display.get_repr(v.__doc__, limit=150) if v.__doc__ is not None else 'No docs for this.'}").to_list()
    main_option = f"RUN AS MAIN -- {tb.Display.get_repr(module.__doc__, limit=150) if module.__doc__ is not None else 'No docs for this.'}"
    options.append(main_option)
    choice_function = display_options(msg="Choose a function to run", options=options, fzf=True, multi=False)
    assert isinstance(choice_function, str), f"choice_function must be a string. Got {type(choice_function)}"
    choice_function = choice_function.split(' -- ')[0]
    return module, choice_function


def interactively_run_function(func: Callable[[Any], Any]):
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    args = []
    kwargs = {}
    for param in params:
        if param.annotation is not inspect.Parameter.empty: hint = f" ({param.annotation.__name__})"
        else: hint = ""
        if param.default is not inspect.Parameter.empty:
            default = param.default
            value = input(f"Please enter a value for argument `{param.name}` (type = {hint}) (default = {default}) : ")
            if value == "": value = default
        else: value = input(f"Please enter a value for argument `{param.name}` (type = {hint}) : ")
        try:
            if param.annotation is not inspect.Parameter.empty: value = param.annotation(value)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Invalid input: {value} is not of type {param.annotation}") from err
        if param.kind == inspect.Parameter.KEYWORD_ONLY: kwargs[param.name] = value
        else: args.append((param.name, value))
    args_to_kwargs = dict(args)
    return args_to_kwargs, kwargs


def submit_to_cloud(func: Any):
    from crocodile.cluster.template_gooey import main as main_config
    from crocodile.cluster.remote_machine import RemoteMachine, CloudManager, RemoteMachineConfig
    config: RemoteMachineConfig = main_config()
    assert config.cloud_name is not None, f"config.cloud_name must be a string. Got {type(config.cloud_name)}"
    m = RemoteMachine(func=func, func_kwargs=None, config=config)
    _res = m.submit_to_cloud(split=int(input("Number of job splits: ")), cm=CloudManager(max_jobs=1, cloud=config.cloud_name))

def run_on_remote(func_file: str, args: argparse.Namespace):
    host = choose_ssh_host(multi=False)
    assert isinstance(host, str), f"host must be a string. Got {type(host)}"
    from crocodile.cluster.remote_machine import RemoteMachine, RemoteMachineConfig
    config = RemoteMachineConfig(copy_repo=True, update_repo=False, update_essential_repos=True,
                                 notify_upon_completion=True, ssh_params=dict(host=host),
                                 # to_email=None, email_config_name='enaut',
                                 data=[],
                                 ipython=False, interactive=args.interactive, pdb=False, pudb=args.debug, wrap_in_try_except=False,
                                 transfer_method="sftp")
    m = RemoteMachine(func=func_file, func_kwargs=None, config=config)
    m.run()


if __name__ == '__main__':
    main()
