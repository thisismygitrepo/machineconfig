from typing import Optional
import os
from pathlib import Path
import platform


def parse_pyfile(file_path: str):
    print(f"🔍 Loading {file_path} ...")
    from typing import NamedTuple

    args_spec = NamedTuple("args_spec", [("name", str), ("type", str), ("default", Optional[str])])
    func_args: list[list[args_spec]] = [[]]  # this firt prepopulated dict is for the option 'RUN AS MAIN' which has no args
    import ast

    parsed_ast = ast.parse(Path(file_path).read_text(encoding="utf-8"))
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


def wrap_import_in_try_except(import_line: str, pyfile: str, repo_root: Optional[str] = None) -> None:
    try:
        exec(import_line)  # type: ignore
    except (ImportError, ModuleNotFoundError) as ex:
        print(fr"❌ Failed to import `{pyfile}` as a module: {ex} ")
        print("⚠️ Attempting import with ad-hoc `$PATH` manipulation. DO NOT pickle any objects in this session as correct deserialization cannot be guaranteed.")
        import sys
        sys.path.append(str(Path(pyfile).parent))
        if repo_root is not None:
            sys.path.append(repo_root)
        exec(f"from {Path(pyfile).stem} import *")
        print(fr"✅ Successfully imported `{pyfile}`")


def add_to_path(path_variable: str, directory: str) -> str:
    """
    Generate shell script to add directory to path_variable.
    Handles both Windows (cmd) and Unix-like systems (bash/zsh).
    Checks if variable exists before appending, otherwise creates it.
    """
    system = platform.system()
    
    if system == "Windows":
        script = f"""# Check if {path_variable} is defined
if (Test-Path env:{path_variable}) {{
    Write-Host "Adding {directory} to existing {path_variable}"
    $currentValue = [Environment]::GetEnvironmentVariable("{path_variable}", "User")
    $newValue = "$currentValue;{directory}"
    [Environment]::SetEnvironmentVariable("{path_variable}", $newValue, "User")
    $env:{path_variable} = $newValue
}} else {{
    Write-Host "Creating new {path_variable} variable"
    [Environment]::SetEnvironmentVariable("{path_variable}", "{directory}", "User")
    $env:{path_variable} = "{directory}"
}}
Write-Host "{path_variable} is now: $env:{path_variable}\""""
        return script
    else:
        script = f"""#!/bin/bash
# Check if {path_variable} is defined and not empty
if [ -z "${{{path_variable}}}" ]; then
    echo "Creating new {path_variable} variable"
    export {path_variable}="{directory}"
else
    echo "Adding {directory} to existing {path_variable}"
    export {path_variable}="${{{path_variable}}}:{directory}"
fi
echo "{path_variable} is now: ${{{path_variable}}}"
"""
        return script

