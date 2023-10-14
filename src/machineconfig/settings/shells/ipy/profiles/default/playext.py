
"""G
"""
# pylint: off

# from crocodile.core import Display
from IPython.core.magic import register_line_magic
# from IPython import get_ipython

# get_ipython()

@register_line_magic("play")  # type: ignore
def run_python_file_in_this_namespace(a_path: str):
    from machineconfig.utils.utils import match_file_name
    import platform
    from crocodile.file_management import P
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
    from IPython.terminal.embed import InteractiveShellEmbed

    ipshell = InteractiveShellEmbed()
    _result = path.as_posix()
    # %run $result  # pylint: disable=E0001 # type: ignore  # noqa: #999
    ipshell.run_line_magic(magic_name="run", line="$_result")


@register_line_magic("mplay")  # type: ignore
def import_python_file_in_this_namespace(a_path: str):
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
    from IPython.terminal.embed import InteractiveShellEmbed
    ipshell = InteractiveShellEmbed()
    _result = P.tmp().joinpath(f"tmp_scripts/python/{randstr()}.py").write_text(f"""
import sys
sys.path.append(r'{path.parent}')
from {path.stem} import *
""")
    print(f"IPyExtention: Remember that reload fails for imported moules that import other varying modules.")
    ipshell.run_line_magic(magic_name="run", line="$_result")
