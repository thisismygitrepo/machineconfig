from crocodile.core import List as L
from crocodile.file_management import P
import platform
import subprocess
from typing import Optional, TypeVar
from machineconfig.utils.utils_options import check_tool_exists, choose_one_option

T = TypeVar("T")

def sanitize_path(a_path: P) -> P:
    path = P(a_path)
    if path.as_posix().startswith("/home"):
        if platform.system() == "Windows":  # path copied from Linux to Windows
            path = P.home().joinpath(*path.parts[3:])  # exclude /home/username
            assert path.exists(), f"File not found: {path}"
            print(f"""
{'=' * 60}
🔗 PATH MAPPING | Linux → Windows: `{a_path}` ➡️ `{path}`
{'=' * 60}
""")
        elif platform.system() == "Linux" and P.home().as_posix() not in path.as_posix():  # copied from Linux to Linux with different username
            path = P.home().joinpath(*path.parts[3:])  # exclude /home/username (three parts: /, home, username)
            assert path.exists(), f"File not found: {path}"
            print(f"""
{'=' * 60}
🔗 PATH MAPPING | Linux → Linux: `{a_path}` ➡️ `{path}`
{'=' * 60}
""")
    elif path.as_posix().startswith("C:"):
        if platform.system() == "Linux":  # path copied from Windows to Linux
            xx = str(a_path).replace("\\", "/")
            path = P.home().joinpath(*P(xx).parts[3:])  # exclude C:\Users\username
            assert path.exists(), f"File not found: {path}"
            print(f"""
{'=' * 60}
🔗 PATH MAPPING | Windows → Linux: `{a_path}` ➡️ `{path}`
{'=' * 60}
""")
        elif platform.system() == "Windows" and P.home().as_posix() not in path.as_posix():  # copied from Windows to Windows with different username
            path = P.home().joinpath(*path.parts[2:])
            assert path.exists(), f"File not found: {path}"
            print(f"""
{'=' * 60}
🔗 PATH MAPPING | Windows → Windows: `{a_path}` ➡️ `{path}`
{'=' * 60}
""")
    return path.expanduser().absolute()

def match_file_name(sub_string: str, search_root: Optional[P] = None) -> P:
    """Look up current directory for file name that matches the passed substring."""
    search_root_obj = search_root if search_root is not None else P.cwd()
    search_root_obj = search_root_obj.absolute()
    print(f"""
{'=' * 60}
🔍 SEARCH | Looking for '{sub_string}' in {search_root_obj}
{'=' * 60}
""")

    search_root_objects = search_root_obj.search("*", not_in=["links", ".venv", ".git", ".idea", ".vscode", "node_modules", "__pycache__"])
    search_results: L[P] = L([a_search_root_obj.search(f"*{sub_string}*", r=True) for a_search_root_obj in search_root_objects]).reduce(lambda x, y: x + y)  # type: ignore
    search_results = search_results.filter(lambda x: x.suffix in (".py", ".sh", ".ps1"))

    if len(search_results) == 1:
        path_obj = search_results.list[0]
    elif len(search_results) > 1:
        msg = "Search results are ambiguous or non-existent, choose manually:"
        print(f"""
⚠️  WARNING | {msg}
{'=' * 60}
""")
        choice = choose_one_option(msg=msg, options=search_results.list, fzf=True)
        path_obj = P(choice)
    else:
        # let's do a final retry with sub_string.small()
        sub_string_small = sub_string.lower()
        if sub_string_small != sub_string:
            print(f"""
🔄 RETRY | Searching with lowercase letters
{'=' * 60}
""")
            return match_file_name(sub_string=sub_string_small)
        from git.repo import Repo
        from git.exc import InvalidGitRepositoryError
        try:
            repo = Repo(search_root_obj, search_parent_directories=True)
            repo_root_dir = P(repo.working_dir)
            if repo_root_dir != search_root_obj:  # may be user is in a subdirectory of the repo root, try with root dir.
                print(f"""
🔄 RETRY | Searching from repository root instead of current directory
{'=' * 60}
""")
                return match_file_name(sub_string=sub_string, search_root=repo_root_dir)
            else:
                search_root_obj = repo_root_dir
        except InvalidGitRepositoryError:
            pass

        if check_tool_exists(tool_name="fzf"):
            try:
                print(f"""
🔍 SEARCH STRATEGY | Using fd to search for '{sub_string}' in '{search_root_obj}' ...
{'=' * 60}
""")
                fzf_cmd = f"cd '{search_root_obj}'; fd --type f --strip-cwd-prefix | fzf --filter={sub_string}"
                search_res = subprocess.run(fzf_cmd, stdout=subprocess.PIPE, text=True, check=True, shell=True).stdout.split("\n")[:-1]
            except subprocess.CalledProcessError as cpe:
                print(f"""
❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'.
{cpe}
{'=' * 60}
""")
                msg = f"""
{'=' * 60}
💥 FILE NOT FOUND | Path {sub_string} does not exist. No search results
{'=' * 60}
"""
                raise FileNotFoundError(msg) from cpe

            if len(search_res) == 1: return search_root_obj.joinpath(search_res[0])
            else:
                print(f"""
🔍 SEARCH STRATEGY | Trying with raw fzf search ...
{'=' * 60}
""")
                try:
                    res = subprocess.run(f"cd '{search_root_obj}'; fd | fzf --query={sub_string}", check=True, stdout=subprocess.PIPE, text=True, shell=True).stdout.strip()
                except subprocess.CalledProcessError as cpe:
                    print(f"""
❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'. {cpe}
{'=' * 60}
""")
                    msg = f"""
{'=' * 60}
💥 FILE NOT FOUND | Path {sub_string} does not exist. No search results
{'=' * 60}
"""
                    raise FileNotFoundError(msg) from cpe
                return search_root_obj.joinpath(res)

        msg = f"""
{'=' * 60}
💥 FILE NOT FOUND | Path {sub_string} does not exist. No search results
{'=' * 60}
"""
        raise FileNotFoundError(msg)
    print(f"""
{'=' * 60}
✅ MATCH FOUND | `{sub_string}` ➡️ `{path_obj}`
{'=' * 60}
""")
    return path_obj
