from crocodile.core import List as L
from crocodile.file_management import P
from machineconfig.utils.options import check_tool_exists, choose_one_option
from rich.console import Console
from rich.panel import Panel
import platform
import subprocess
from typing import TypeVar
from pathlib import Path


T = TypeVar("T")
console = Console()

def sanitize_path(a_path: P) -> P:
    path = P(a_path)
    if path.as_posix().startswith("/home") or path.as_posix().startswith("/Users"):
        if platform.system() == "Windows":  # path copied from Linux/Mac to Windows
            # For Linux: /home/username, for Mac: /Users/username
            skip_parts = 3 if path.as_posix().startswith("/home") else 3  # Both have 3 parts to skip
            path = P.home().joinpath(*path.parts[skip_parts:])
            assert path.exists(), f"File not found: {path}"
            source_os = "Linux" if a_path.as_posix().startswith("/home") else "macOS"
            console.print(Panel(f"🔗 PATH MAPPING | {source_os} → Windows: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
        elif platform.system() in ["Linux", "Darwin"] and P.home().as_posix() not in path.as_posix():  # copied between Unix-like systems with different username
            skip_parts = 3  # Both /home/username and /Users/username have 3 parts to skip
            path = P.home().joinpath(*path.parts[skip_parts:])
            assert path.exists(), f"File not found: {path}"
            current_os = "Linux" if platform.system() == "Linux" else "macOS"
            source_os = "Linux" if a_path.as_posix().startswith("/home") else "macOS"
            console.print(Panel(f"🔗 PATH MAPPING | {source_os} → {current_os}: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
    elif path.as_posix().startswith("C:"):
        if platform.system() in ["Linux", "Darwin"]:  # path copied from Windows to Linux/Mac
            xx = str(a_path).replace("\\\\", "/")
            path = P.home().joinpath(*P(xx).parts[3:])  # exclude C:\\Users\\username
            assert path.exists(), f"File not found: {path}"
            target_os = "Linux" if platform.system() == "Linux" else "macOS"
            console.print(Panel(f"🔗 PATH MAPPING | Windows → {target_os}: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
        elif platform.system() == "Windows" and P.home().as_posix() not in path.as_posix():  # copied from Windows to Windows with different username
            path = P.home().joinpath(*path.parts[2:])
            assert path.exists(), f"File not found: {path}"
            console.print(Panel(f"🔗 PATH MAPPING | Windows → Windows: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
    return path.expanduser().absolute()


def find_scripts(root: Path, name_substring: str) -> list[Path]:
    scripts = []
    for entry in root.iterdir():
        if entry.is_dir():
            if entry.name in {".links", ".venv", ".git", ".idea", ".vscode", "node_modules", "__pycache__"}:
                # prune this entire subtree
                continue
            tmp = find_scripts(entry, name_substring)
            scripts.extend(tmp)
        elif entry.is_file() and entry.suffix in {".py", ".sh", ".ps1"}:
            if name_substring.lower() in entry.name.lower():
                scripts.append(entry)
    return scripts


def match_file_name(sub_string: str, search_root: P) -> P:
    search_root_obj = search_root.absolute()
    # assume subscript is filename only, not a sub_path. There is no need to fzf over the paths.
    all_scripts = find_scripts(search_root_obj, sub_string)
    if len(all_scripts) == 1: return P(all_scripts[0])
    console.print(Panel(f"Partial filename match with case-insensitivity failed. This generated #{len(all_scripts)} results.\n🔍 SEARCH | Looking for '{sub_string}' in {search_root_obj}", title="Search", expand=False))
    if len(all_scripts) > 1:
        print("Try to narrow down the search by case-sensitivity.")
        # let's see if avoiding .lower() helps narrowing down to one result
        reduced_scripts = [script for script in all_scripts if sub_string in script.name]
        if len(reduced_scripts) == 1: return P(reduced_scripts[0])



    try:
        fzf_cmd = f"cd '{search_root_obj}'; fd --type file --strip-cwd-prefix | fzf --ignore-case --exact --query={sub_string}"
        console.print(Panel(f"🔍 SEARCH STRATEGY | Using fd to search for '{sub_string}' in '{search_root_obj}' ...\n{fzf_cmd}", title="Search Strategy", expand=False))
        search_res_raw = subprocess.run(fzf_cmd, stdout=subprocess.PIPE, text=True, check=True, shell=True,).stdout
        search_res = search_res_raw.strip().split("\\n")[:-1]
    except subprocess.CalledProcessError as cpe:
        console.print(Panel(f"❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'.\n{cpe}", title="Error", expand=False))
        import sys
        sys.exit(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results.")
    if len(search_res) == 1: return search_root_obj.joinpath(search_res_raw)

    print(f"⚠️ WARNING | Multiple search results found for `{sub_string}`\n'{search_res_raw}'")
    cmd = f"cd '{search_root_obj}'; fd --type file | fzf --select-1 --query={sub_string}"
    console.print(Panel(f"🔍 SEARCH STRATEGY | Trying with raw fzf search ...\n{cmd}", title="Search Strategy", expand=False))
    try:
        res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True, shell=True).stdout.strip()
    except subprocess.CalledProcessError as cpe:
        console.print(Panel(f"❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'. {cpe}", title="Error", expand=False))
        msg = Panel(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results", title="File Not Found", expand=False)
        raise FileNotFoundError(msg) from cpe
    return search_root_obj.joinpath(res)

def match_file_name_(sub_string: str, search_root: P) -> P:
    """Look up current directory for file name that matches the passed substring."""
    search_root_obj = search_root.absolute()
    console.print(Panel(f"🔍 SEARCH | Looking for '{sub_string}' in {search_root_obj}", title="Search", expand=False))

    search_root_objects = search_root_obj.search("*", not_in=[".links", ".venv", ".git", ".idea", ".vscode", "node_modules", "__pycache__"], folders=True, files=False)
    search_results: L[P] = L()
    for a_search_root_obj in search_root_objects:
        search_results.extend(a_search_root_obj.search(f"*{sub_string}*", r=True))
    search_results.extend(search_root_obj.search(f"*{sub_string}*", r=False, files=True, folders=False))
    if len(search_results) > 0:
        search_results = search_results.reduce(lambda x, y: x + y)  # type: ignore
    else:
        pass
    search_results = search_results.filter(lambda x: x.suffix in (".py", ".sh", ".ps1"))
    if len(search_results) == 1:
        path_obj = search_results.list[0]
    elif len(search_results) > 1:
        msg = "Search results are ambiguous or non-existent, choose manually:"
        console.print(Panel(f"⚠️ WARNING | {msg}", title="Warning", expand=False))
        choice = choose_one_option(msg=msg, options=search_results.list, fzf=True)
        path_obj = P(choice)
    else:
        if sub_string.lower() != sub_string:  # its worth it to retry with lowercase
            console.print(Panel("🔄 RETRY | Searching with lowercase letters", title="Retry", expand=False))
            return match_file_name(sub_string=sub_string.lower(), search_root=search_root_obj)
        from git.repo import Repo
        from git.exc import InvalidGitRepositoryError
        try:
            repo = Repo(search_root_obj, search_parent_directories=True)
            repo_root_dir = P(repo.working_dir)
            if repo_root_dir != search_root_obj:  # may be user is in a subdirectory of the repo root, try with root dir.
                console.print(Panel("🔄 RETRY | Searching from repository root instead of current directory", title="Retry", expand=False))
                return match_file_name(sub_string=sub_string, search_root=repo_root_dir)
            else:
                search_root_obj = repo_root_dir
        except InvalidGitRepositoryError:
            pass

        if check_tool_exists(tool_name="fzf"):
            try:
                fzf_cmd = f"cd '{search_root_obj}'; fd --type file --strip-cwd-prefix | fzf  --delimiter='/' --nth=-1 --filter={sub_string}"
                console.print(Panel(f"🔍 SEARCH STRATEGY | Using fd to search for '{sub_string}' in '{search_root_obj}' ...\n{fzf_cmd}", title="Search Strategy", expand=False))
                search_res_raw = subprocess.run(fzf_cmd, stdout=subprocess.PIPE, text=True, check=True, shell=True).stdout
                search_res = search_res_raw.strip().split("\\n")[:-1]
            except subprocess.CalledProcessError as cpe:
                console.print(Panel(f"❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'.\n{cpe}", title="Error", expand=False))
                import sys
                sys.exit(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results.")
            if len(search_res) == 1: return search_root_obj.joinpath(search_res_raw)
            else:
                print(f"⚠️ WARNING | Multiple search results found for '{search_res}':")
                cmd = f"cd '{search_root_obj}'; fd --type file | fzf --select-1 --query={sub_string}"
                console.print(Panel(f"🔍 SEARCH STRATEGY | Trying with raw fzf search ...\n{cmd}", title="Search Strategy", expand=False))
                try:
                    res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True, shell=True).stdout.strip()
                except subprocess.CalledProcessError as cpe:
                    console.print(Panel(f"❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'. {cpe}", title="Error", expand=False))
                    msg = Panel(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results", title="File Not Found", expand=False)
                    raise FileNotFoundError(msg) from cpe
                return search_root_obj.joinpath(res)

        msg = Panel(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results", title="File Not Found", expand=False)
        raise FileNotFoundError(msg)
    console.print(Panel(f"✅ MATCH FOUND | `{sub_string}` ➡️ `{path_obj}`", title="Match Found", expand=False))
    return path_obj
