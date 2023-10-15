
"""G
"""

from IPython.core.magic import register_line_magic


@register_line_magic("play")  # type: ignore
def run_python_file_in_this_namespace(a_path: str, module: bool = False):
    from machineconfig.utils.utils import match_file_name
    import platform
    from crocodile.file_management import P, randstr
    path = P(a_path)
    if not path.exists():  # path copied from different OS
        if path.as_posix().startswith("/home") and platform.system() == "Windows":  # path copied from Linux
            path = P.home().joinpath(*path.parts[2:])  # exlcude /home/username
            assert path.exists(), f"File not found: {path}"
            print(f"\n{'--' * 50}\n🔗 Mapped `{a_path}` ➡️ `{path}`\n{'--' * 50}\n")
        elif path.as_posix().startswith("C:") and platform.system() == "Linux":  # path copied from Windows
            path = P.home().joinpath(*path.parts[3:])  # exlcude C:\Users\username
            assert path.exists(), f"File not found: {path}"
            print(f"\n{'--' * 50}\n🔗 Mapped `{a_path}` ➡️ `{path}`\n{'--' * 50}\n")
        else:
            path = match_file_name(a_path)
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
