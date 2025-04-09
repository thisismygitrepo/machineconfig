"""G

"""

from IPython.core.magic import register_line_magic
from crocodile.core import Struct, randstr
from crocodile.file_management import P
from typing import Any


def get_names():
    res: dict[str, list[str]] = {}
    for item in globals().keys():
        if item.startswith("_") or item in ("open", "In", "Out", "quit", "exit", "get_ipython"):
            continue
        if item in ("P", "randstr", "Struct", "print_code", "print_dir_func", "print_program_func", "run_python_file_in_this_namespace"):
            continue
        type_ = repr(type(eval(item)))  # type: ignore  # pylint: disable=eval-used
        if "typing." in type_: continue
        if type_ in res: res[type_].append(item)
        else: res[type_] = [item]
    return res


@register_line_magic("codei")  # type: ignore
def print_code_interactive(_):
    res = get_names()
    from machineconfig.utils.utils import choose_one_option
    choice = choose_one_option(options=res["<class 'function'>"], msg="Choose a type to inspect", fzf=True)
    obj = eval(choice, globals(), locals())  # type: ignore  # pylint: disable=eval-used
    from rich.syntax import Syntax
    import inspect
    q: str = inspect.getsource(obj)
    from rich import console
    console.Console().print(Syntax(code=q, lexer="python"))


@register_line_magic("print_dir")  # type: ignore
def print_dir_func(line: Any):
    """Pretty print and categorize dir() output."""
    _ = line  # ipython caller assumes there is at least one argument, an passes '' worstcase.
    res = get_names()
    Struct(dictionary=res).print(as_config=True, title="""
📂 Objects Defined in Current Directory
=======================================
""")


@register_line_magic("code")  # type: ignore
def print_program_func(obj_str: str):
    """Inspect the code of an object."""
    obj = eval(obj_str, globals(), locals())  # type: ignore  # pylint: disable=eval-used
    from rich.syntax import Syntax
    import inspect
    q: str = inspect.getsource(obj)
    from rich import console
    console.Console().print(Syntax(code=q, lexer="python"))


@register_line_magic("play")  # type: ignore
def run_python_file_in_this_namespace(a_path: str, module: bool=False):
    """Given a potentially dirty path of python file, run it in this namespace."""
    from machineconfig.utils.utils import match_file_name, sanitize_path
    path = sanitize_path(P(a_path))
    if not path.exists():
        path = match_file_name(a_path)
    from IPython import get_ipython  # type: ignore  # this gets the same instance, its in the namespace anyway even if not imported.
    if module:
        code_snippet = f"""
import sys
sys.path.append(r'{path.parent}')
from {path.stem} import *
"""

        result = P.tmp().joinpath(f"tmp_scripts/python/{randstr()}.py").write_text(code_snippet)
        print("""💡 IPyExtension: Remember that reload fails for imported modules that import other varying modules.""")
        get_ipython().run_line_magic(magic_name="load", line=result)  # type: ignore
        return

    result = path.as_posix()
    print(f"➡️ Running magic: %run {result}")
    get_ipython().run_line_magic(magic_name="run", line=result)  # type: ignore
    globals().update(locals())
