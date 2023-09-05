
"""
fire
"""

import crocodile.toolbox as tb
import platform
from machineconfig.utils.utils import display_options, PROGRAM_PATH, choose_ssh_host
# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for display_options build TUI
# https://github.com/chriskiehl/Gooey build commandline interface
import inspect
from typing import Callable, Any
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="The directory containing the jobs", default=".")
    parser.add_argument("-v", "--ve", type=str, help="virtual enviroment name", default="")
    # optional flag for interactivity
    parser.add_argument("--interactive", "-i", action="store_true", help="Whether to run the job interactively using IPython")
    parser.add_argument("--debug", "-d", action="store_true", help="debug")
    parser.add_argument("--choose_function", "-c", action="store_true", help="debug")
    parser.add_argument("--remote", "-r", action="store_true", help="launch on a remote machine")
    parser.add_argument("--module", "-m", action="store_true", help="launch the main file")
    parser.add_argument("--history", "-H", action="store_true", help="choose from history")

    args = parser.parse_args()

    jobs_dir = tb.P(args.path).expanduser().absolute()

    print(f"Seaching recursively for all python file in directory `{jobs_dir}`")
    py_files = jobs_dir.search(pattern="*.py", not_in=["__init__.py"], r=True).to_list()
    choice_file = display_options(msg="Choose a file to run", options=py_files, fzf=True, multi=False)
    assert isinstance(choice_file, str), f"choice_file must be a string. Got {type(choice_file)}"

    if args.choose_function:
        assert isinstance(choice_file, str), f"choice_file must be a string. Got {type(choice_file)}"
        _module, choice_function = choose_function(choice_file)
        # if choice_function != "RUN AS MAIN":
            # kgs1, _ = interactively_run_function(module[choice_function])
            # " ".join([f"--{k} {v}" for k, v in kgs1.items()])
    else:
        choice_function = None

    if args.module:
        txt: str = f"""
import sys
sys.path.append(r'{tb.P(choice_file).parent}')
from {tb.P(choice_file).stem} import *
"""
        if choice_function is not None:
            txt = txt + f"""
{choice_function}()
"""
        txt = txt + f"""
from machineconfig.utils.utils import print_programming_script
print_programming_script(r'''{txt}''', lexer='python', desc='Imported Script')
"""
        choice_file = tb.P.tmp().joinpath(f'tmp_scripts/python/{tb.randstr()}.py').create(parents_only=True).write_text(txt)

    if args.interactive is False: exe = "python"
    else: exe = "ipython -i"

    # determining basic command structure: putting together exe & choice_file & choice_function & pdb
    if args.debug:
        if platform.system() == "Windows":
            command = f"{exe} -m pdb {choice_file} "  # pudb is not available on windows machines, use poor man's debugger instead.
        elif platform.system() in ["Linux", "Darwin"]:
            command = f"{exe} -m pudb {choice_file} "  # TODO: functions not supported yet in debug mode.
        else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
    elif choice_function is not None:
        command = f"{exe} -m fire {choice_file} {choice_function} "
    else:
        command = f"{exe} {choice_file} "

    # try:
    #     ve_name = get_current_ve()
    #     exe = f". activate_ve {ve_name}; {exe}"
    # except NotImplementedError:
    #     print(f"Failed to detect virtual enviroment name.")
    #     pass
    command = f"deactivate;. activate_ve {args.ve}; {command}"

    # if args.remote: return run_on_remote(choice_file, args=args)
    try: tb.install_n_import("clipboard").copy(command)
    except Exception as ex: print(f"Failed to copy command to clipboard. {ex}")
    # CONFIG_PATH
    # TODO: send this command to terminal history. In powershell & bash there is no way to do it with a command other than goiing to history file. In Mcfly there is a way but its linux only tool.
    print("\n", command, "\n\n\n")
    # if platform.system() == "Windows": command = f" ({command}) | Add-History  -PassThru "
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
