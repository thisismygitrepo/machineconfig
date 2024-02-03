
"""G
"""

from IPython.core.magic import register_line_magic
from crocodile.file_management import P, randstr, Struct
# from typing import Any


@register_line_magic("print_dir")  # type: ignore
def print_dir():
    """Pretty print and categorize dir() output."""
    res: dict[str, list[str]] = {}
    for item in globals().keys():
        if item.startswith("_"): continue
        type_ = repr(type(eval(item)))  # type: ignore  # pylint: disable=eval-used
        if "typing." in type_: continue
        if type_ in res: res[type_].append(item)
        else: res[type_] = [item]
    Struct(dictionary=res).print(as_config=True, title="Objects defined in current dir")


@register_line_magic("code")  # type: ignore
def print_program(obj_str: str):
    """Inspect the code of an object."""
    from rich.syntax import Syntax
    import inspect
    obj = eval(obj_str, globals(), locals())  # type: ignore  # pylint: disable=eval-used
    q: str = inspect.getsource(obj)
    from rich import console
    console.Console().print(Syntax(code=q, lexer="python"))


@register_line_magic("play")  # type: ignore
def run_python_file_in_this_namespace(a_path: str, module: bool = False):
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
        # print(f"IPyExtention: Remember that reload fails for imported moules that import other varying modules.")
        get_ipython().run_line_magic(magic_name="load", line=result)  # type: ignore
        return

    result = path.as_posix()
    # from IPython.terminal.embed import InteractiveShellEmbed
    # from IPython.terminal.interactiveshell import TerminalInteractiveShell
    # shell = TerminalInteractiveShell()  # ❌ don't start a new instance
    # %run $result  # pylint: disable=E0001 # type: ignore  # noqa: #999
    print(f"➡️ Running magic: %run {result}")
    get_ipython().run_line_magic(magic_name="run", line=result)  # type: ignore
    # shell.run_line_magic(magic_name="load", line="$_result")
    # update gobal namespace
    globals().update(locals())
