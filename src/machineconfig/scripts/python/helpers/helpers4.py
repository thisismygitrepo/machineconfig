from typing import Any, Callable, Optional
import inspect
import os

# import argparse
from machineconfig.utils.path_reduced import PathExtended as PathExtended
# from machineconfig.utils.utils import choose_ssh_host


def search_for_files_of_interest(path_obj: PathExtended):
    if path_obj.joinpath(".venv").exists():
        path_objects = path_obj.search("*", not_in=[".venv"])
        files: list[PathExtended] = []
        for a_path_obj in path_objects:
            files += search_for_files_of_interest(path_obj=a_path_obj)
        return files
    if path_obj.is_file():
        return [path_obj]
    py_files = path_obj.search(pattern="*.py", not_in=["__init__.py"], r=True)
    ps_files = path_obj.search(pattern="*.ps1", r=True)
    sh_files = path_obj.search(pattern="*.sh", r=True)
    files = py_files + ps_files + sh_files
    return files


def convert_kwargs_to_fire_kwargs_str(kwargs: dict[str, Any]) -> str:
    # https://google.github.io/python-fire/guide/
    # https://github.com/google/python-fire/blob/master/docs/guide.md#argument-parsing
    if not kwargs:  # empty dict
        kwargs_str = ""
    else:
        # For fire module, all keyword arguments should be passed as --key value pairs
        tmp_list: list[str] = []
        for k, v in kwargs.items():
            tmp_list.append(f"--{k} {v}")
        kwargs_str = " " + " ".join(tmp_list) + " "
    return kwargs_str


def parse_pyfile(file_path: str):
    print(f"🔍 Loading {file_path} ...")
    from typing import NamedTuple

    args_spec = NamedTuple("args_spec", [("name", str), ("type", str), ("default", Optional[str])])
    func_args: list[list[args_spec]] = [[]]  # this firt prepopulated dict is for the option 'RUN AS MAIN' which has no args
    import ast

    parsed_ast = ast.parse(PathExtended(file_path).read_text(encoding="utf-8"))
    functions = [node for node in ast.walk(parsed_ast) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    module__doc__ = ast.get_docstring(parsed_ast)
    main_option = f"RUN AS MAIN -- {module__doc__ if module__doc__ is not None else 'NoDocs'}"
    options = [main_option]
    for function in functions:
        if function.name.startswith("__") and function.name.endswith("__"):
            continue
        if any(arg.arg == "self" for arg in function.args.args):
            continue
        if any(arg.arg == "self" for arg in function.args.args):
            continue
        doc_string_tmp: str | None = ast.get_docstring(function)
        if doc_string_tmp is None:
            doc_string = "NoDocs"
        else:
            doc_string = doc_string_tmp.replace("\n", " ")
        options.append(f"{function.name} -- {', '.join([arg.arg for arg in function.args.args])} -- {doc_string}")
        tmp = []
        for idx, arg in enumerate(function.args.args):
            if arg.annotation is not None:
                try:
                    type_ = arg.annotation.__dict__["id"]
                except KeyError as ke:
                    type_ = "Any"  # e.g. a callable object
                    _ = ke
            else:
                type_ = "Any"
            default_tmp = function.args.defaults[idx] if idx < len(function.args.defaults) else None
            if default_tmp is None:
                default = None
            else:
                if hasattr(default_tmp, "__dict__"):
                    default = default_tmp.__dict__.get("value", None)
                else:
                    default = None
            tmp.append(args_spec(name=arg.arg, type=type_, default=default))
        func_args.append(tmp)
    return options, func_args


def interactively_run_function(func: Callable[[Any], Any]):
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    args = []
    kwargs = {}
    for param in params:
        if param.annotation is not inspect.Parameter.empty:
            hint = f" ({param.annotation.__name__})"
        else:
            hint = ""
        if param.default is not inspect.Parameter.empty:
            default = param.default
            value = input(f"Please enter a value for argument `{param.name}` (type = {hint}) (default = {default}) : ")
            if value == "":
                value = default
        else:
            value = input(f"Please enter a value for argument `{param.name}` (type = {hint}) : ")
        try:
            if param.annotation is not inspect.Parameter.empty:
                value = param.annotation
        except (TypeError, ValueError) as err:
            raise ValueError(f"Invalid input: {value} is not of type {param.annotation}") from err
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            kwargs[param.name] = value
        else:
            args.append((param.name, value))
    args_to_kwargs = dict(args)
    return args_to_kwargs, kwargs


def get_attrs_recursively(obj: Any):
    if hasattr(obj, "__dict__"):
        res = {}
        for k, v in obj.__dict__.items():
            res[k] = get_attrs_recursively(v)
        return res
    return obj


# def run_on_remote(func_file: str, args: argparse.Namespace):
#     host = choose_ssh_host(multi=False)
#     assert isinstance(host, str), f"host must be a string. Got {type(host)}"
#     from machineconfig.cluster.remote_machine import RemoteMachine, RemoteMachineConfig
#     config = RemoteMachineConfig(copy_repo=True, update_repo=False, update_essential_repos=True,
#                                  notify_upon_completion=True, ssh_params=dict(host=host),
#                                  # to_email=None, email_config_name='enaut',
#                                  data=[],
#                                  ipython=False, interactive=args.interactive, pdb=False, pudb=args.debug, wrap_in_try_except=False,
#                                  transfer_method="sftp")
#     m = RemoteMachine(func=func_file, func_kwargs=None, config=config)
#     m.run()


def find_repo_root_path(start_path: str) -> Optional[str]:
    root_files = ["setup.py", "pyproject.toml", ".git"]
    path: str = start_path
    trials = 0
    root_path = os.path.abspath(os.sep)
    while path != root_path and trials < 20:
        for root_file in root_files:
            if os.path.exists(os.path.join(path, root_file)):
                # print(f"Found repo root path: {path}")
                return path
        path = os.path.dirname(path)
        trials += 1
    return None


def get_import_module_code(module_path: str):
    root_path = find_repo_root_path(module_path)
    if root_path is None:  # just make a desperate attempt to import it
        module_name = module_path.lstrip(os.sep).replace(os.sep, ".")
        if module_name.endswith(".py"):
            module_name = module_name[:-3]
    else:
        relative_path = module_path.replace(root_path, "")
        module_name = relative_path.lstrip(os.sep).replace(os.sep, ".")
        if module_name.endswith(".py"):
            module_name = module_name[:-3]
        # module_name = module_name.replace("src.", "").replace("myresources.", "").replace("resources.", "").replace("source.", "")
        if module_name.startswith("src."):
            module_name = module_name[4:]
        if module_name.startswith("myresources."):
            module_name = module_name[12:]
        if module_name.startswith("resources."):
            module_name = module_name[10:]
        if module_name.startswith("source."):
            module_name = module_name[7:]
    if any(char in module_name for char in "- :/\\"):
        module_name = "IncorrectModuleName"
    # TODO: use py_compile to check if the statement is valid code to avoid syntax errors that can't be caught.
    return f"from {module_name} import *"
