
"""G
"""

from IPython.core.magic import register_line_magic
from crocodile.file_management import P, randstr, Struct
from typing import Any


@register_line_magic("print_dir")  # type: ignore
def print_dir():
    res: dict[str, list[str]] = {}
    for item in dir():
        if item.startswith("_"): continue
        type_ = repr(type(eval(item)))
        if "typing." in type_: continue
        if type_ in res: res[type_].append(item)
        else: res[type_] = [item]
    Struct(dictionary=res).print(as_config=True, title="Objects defined in current dir")


@register_line_magic("inspect")  # type: ignore
def inspect(obj: Any):
    from rich.syntax import Syntax
    import inspect
    q: str = inspect.getsource(obj)
    print(Syntax(code=q, lexer="python"))


@register_line_magic("play")  # type: ignore
def run_python_file_in_this_namespace(a_path: str, module: bool = False):
    from machineconfig.utils.utils import match_file_name, sanitize_path
    path = sanitize_path(P(a_path))
    if not path.exists(): path = match_file_name(a_path)
    from IPython import get_ipython  # type: ignore  # this gets the same instance, its in the namespace anyway even if not imported.
    if module:
        code = f"""
import sys
sys.path.append(r'{path.parent}')
from {path.stem} import *
"""

        result = P.tmp().joinpath(f"tmp_scripts/python/{randstr()}.py").write_text(code)
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
    