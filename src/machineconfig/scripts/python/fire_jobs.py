
"""
fire
"""

import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH, choose_ssh_host, match_file_name, sanitize_path
# from crocodile.run import *
# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for display_options build TUI
# https://github.com/chriskiehl/Gooey build commandline interface
import inspect
import platform
import os
from typing import Callable, Any, Optional
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs='?', type=str, help="The directory containing the jobs", default=".")
    parser.add_argument("function", nargs='?', type=str, help="Fuction to run", default=None)
    # parser.add_argument("--function", "-f", type=str, help="The function to run", default="")
    parser.add_argument("--ve", "-v", type=str, help="virtual enviroment name", default="")
    parser.add_argument("--cmd", "-B", action="store_true", help="Create a cmd fire command to launch the the job asynchronously.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Whether to run the job interactively using IPython")
    parser.add_argument("--debug", "-d", action="store_true", help="debug")
    parser.add_argument("--choose_function", "-c", action="store_true", help="debug")
    parser.add_argument("--loop", "-l", action="store_true", help="infinite recusion (runs again after completion)")
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

    path_obj = sanitize_path(tb.P(args.path))
    if not path_obj.exists(): path_obj = match_file_name(args.path)

    if path_obj.is_dir():
        print(f"Seaching recursively for all python file in directory `{path_obj}`")
        py_files = path_obj.search(pattern="*.py", not_in=["__init__.py"], r=True).list
        ps_files = path_obj.search(pattern="*.ps1", r=True).list
        sh_files = path_obj.search(pattern="*.sh", r=True).list
        files = py_files + ps_files + sh_files

        choice_file = display_options(msg="Choose a file to run", options=files, fzf=True, multi=False)
        assert not isinstance(choice_file, list), f"choice_file must be a string. Got {type(choice_file)}"
        choice_file = tb.P(choice_file)
    else:
        choice_file = path_obj

    if choice_file.suffix in [".ps1", ".sh"]:
        PROGRAM_PATH.write_text(f". {choice_file}")
        return

    if args.choose_function or args.submit_to_cloud:

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
    else: choice_function = args.function

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
try:
    {get_import_module_code(str(choice_file))}
except (ImportError, ModuleNotFoundError) as ex:
    print(fr"Failed to import {choice_file} the proper way. {{ex}} ")
    print(fr"The way below is rather hacky and can cause issues in pickling.")
    import sys
    sys.path.append(r'{tb.P(choice_file).parent}')
    from {tb.P(choice_file).stem} import *

"""
        if choice_function is not None:
            txt = txt + f"""
{choice_function}({('**' + str(kwargs)) if kwargs else ''})
"""
        txt = f"""
from machineconfig.utils.utils import print_code
print_code(code=r'''{txt}''', lexer='python', desc='Imported Script')
""" + txt
        choice_file = tb.P.tmp().joinpath(f'tmp_scripts/python/{tb.P(choice_file).parent.name}_{tb.P(choice_file).stem}_{tb.randstr()}.py').create(parents_only=True).write_text(txt)

    # determining basic command structure: putting together exe & choice_file & choice_function & pdb
    if args.debug:
        if platform.system() == "Windows":
            command = f"{exe} -m ipdb {choice_file} "  # pudb is not available on windows machines, use poor man's debugger instead.
        elif platform.system() in ["Linux", "Darwin"]:
            command = f"{exe} -m pudb {choice_file} "  # TODO: functions not supported yet in debug mode.
        else: raise NotImplementedError(f"Platform {platform.system()} not supported.")
    elif choice_function is not None and not args.module:  # if args.module, then kwargs are handled in the impot script, no need to pass them in fire command.
        # https://google.github.io/python-fire/guide/
        tmp = f"'{kwargs}'" if kwargs else ''
        command = f"{exe} -m fire {choice_file} {choice_function} {tmp}"
        # else:
        #     print(f"{kwargs=}")
        #     print(f"{choice_function_args=}")
        # if choice_function != "RUN AS MAIN":
            # kgs1, _ = interactively_run_function(module[choice_function])
            # " ".join([f"--{k} {v}" for k, v in kgs1.items()])
    else:
        if not args.streamlit: command = f"{exe} {choice_file} "
        else:
            if not args.cmd:
                # for .streamlit config to work, it needs to be in the current directory.
                command = f"cd {choice_file.parent}; {exe} {choice_file.name}; cd {tb.P.cwd()}"
            else: command = rf""" cd /d {choice_file.parent} & {exe} {choice_file.name} """
            # command = f"cd {choice_file.parent}; {exe} {choice_file.name}; cd {tb.P.cwd()}"

    if "ipdb" in command: tb.install_n_import("ipdb")
    if "pudb" in command: tb.install_n_import("pudb")

    if not args.cmd:
        command = f". activate_ve {args.ve}; {command}"
    else:
        command = fr"""start cmd -Argument "/k %USERPROFILE%\venvs\{args.ve}\Scripts\activate.bat & {command} " """  # this works from powershell
        # this works from cmd  # command = fr""" start cmd /k "%USERPROFILE%\venvs\{args.ve}\Scripts\activate.bat & {command} " """ # because start in cmd is different from start in powershell (in powershell it is short for Start-Process)

    if args.submit_to_cloud:
        command = f"""
. activate_ve {args.ve}
python -m crocodile.cluster.templates.cli_click --file {choice_file} """
        if choice_function is not None: command += f"--function {choice_function} "
    try: tb.install_n_import("clipboard").copy(command)
    except Exception as ex: print(f"Failed to copy command to clipboard. {ex}")

    if args.loop:
        command = command + f"\n" + f". {PROGRAM_PATH}"

    # TODO: send this command to terminal history. In powershell & bash there is no way to do it with a command other than goiing to history file. In Mcfly there is a way but its linux only tool. # if platform.system() == "Windows": command = f" ({command}) | Add-History  -PassThru "
    print(f"🔥 command:\n{command}\n\n")
    # if platform.system() == "Linux":
    #     command = "timeout 1s aafire -driver slang\nclear\n" + command
    PROGRAM_PATH.write_text(command)


def parse_pyfile(file_path: str):
    print(f"Loading {file_path} ...")
    from typing import NamedTuple
    args_spec = NamedTuple("args_spec", [("name", str), ("type", str), ("default", Optional[str])])
    func_args: list[list[args_spec]] = [[]]  # this firt prepopulated dict is for the option 'RUN AS MAIN' which has no args

    import ast
    parsed_ast = ast.parse(tb.P(file_path).read_text(encoding='utf-8'))
    functions = [
        node
        for node in ast.walk(parsed_ast)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    module__doc__ = ast.get_docstring(parsed_ast)
    main_option = f"RUN AS MAIN -- {tb.Display.get_repr(module__doc__, limit=150) if module__doc__ is not None else 'NoDocs'}"
    options = [main_option]
    for function in functions:
        if function.name.startswith('__') and function.name.endswith('__'): continue
        if any(arg.arg == 'self' for arg in function.args.args): continue
        doc_string_tmp: str | None = ast.get_docstring(function)
        if doc_string_tmp is None: doc_string = "NoDocs"
        else: doc_string = doc_string_tmp.replace('\n', ' ')
        options.append(f"{function.name} -- {', '.join([arg.arg for arg in function.args.args])} -- {doc_string}")
        tmp = []
        for idx, arg in enumerate(function.args.args):
            if arg.annotation is not None:
                try: type_ = arg.annotation.__dict__['id']
                except KeyError as ke:
                    # type_ = arg.annotation.__name__
                    # print(f"Failed to get type for {arg.annotation}. {ke}")
                    # tb.Struct(get_attrs(arg.annotation)).print(as_yaml=True)
                    type_ = "Any"  # e.g. a callable object
                    _ = ke
                    # raise ke
            else: type_ = "Any"
            default_tmp = function.args.defaults[idx] if idx < len(function.args.defaults) else None
            if default_tmp is None: default = None
            else:
                if hasattr(default_tmp, "__dict__"): default = default_tmp.__dict__.get("value", None)
                else: default = None
            tmp.append(args_spec(name=arg.arg, type=type_, default=default))
        func_args.append(tmp)
    return options, func_args


def get_attrs(obj: Any):
    if hasattr(obj, '__dict__'):
        res = {}
        for k, v in obj.__dict__.items():
            res[k] = get_attrs(v)
        return res
    return obj


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


def find_root_path(start_path: str):
    root_files = ['setup.py', 'pyproject.toml', '.git']
    path = start_path
    while path != '/':
        for root_file in root_files:
            if os.path.exists(os.path.join(path, root_file)):
                return path
        path = os.path.dirname(path)
    return None


def get_import_module_code(module_path: str):
    root_path = find_root_path(module_path)
    if root_path is None:  # just make a desperate attempt to import it
        module_name = module_path.lstrip(os.sep).replace(os.sep, '.').replace('.py', '')
        return f"from {module_path} import *"
    relative_path = module_path.replace(root_path, '')
    module_name = relative_path.lstrip(os.sep).replace(os.sep, '.').replace('.py', '')
    module_name = module_name.replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "").replace("resources.", "").replace("source.", "").replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "").replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "").replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "").replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "").replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "").replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "").replace("src.", "").replace("resources.", "").replace("source.", "")
    return f"from {module_name} import *"


if __name__ == '__main__':
    # options, func_args = parse_pyfile(file_path="C:/Users/aalsaf01/code/crocodile/myresources/crocodile/core.py")
    main()
