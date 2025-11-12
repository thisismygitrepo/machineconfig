from machineconfig.utils.source_of_truth import EXCLUDE_DIRS
from rich.console import Console
from rich.panel import Panel
import platform
import subprocess
from pathlib import Path
from typing import Optional

console = Console()


def sanitize_path(a_path: str) -> Path:
    path = Path(a_path)
    if Path.cwd() == Path.home() and not path.exists():
        result = input("Current working directory is home, and passed path is not full path, are you sure you want to continue, [y]/n? ") or "y"
        if result == "y":
            import sys

            sys.exit()
    if path.as_posix().startswith("/home") or path.as_posix().startswith("/Users"):
        if platform.system() == "Windows":  # path copied from Linux/Mac to Windows
            # For Linux: /home/username, for Mac: /Users/username
            skip_parts = 3 if path.as_posix().startswith("/home") else 3  # Both have 3 parts to skip
            path = Path.home().joinpath(*path.parts[skip_parts:])
            assert path.exists(), f"File not found: {path}"
            source_os = "Linux" if path.as_posix().startswith("/home") else "macOS"
            console.print(Panel(f"🔗 PATH MAPPING | {source_os} → Windows: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
        elif platform.system() in ["Linux", "Darwin"] and Path.home().as_posix() not in path.as_posix():  # copied between Unix-like systems with different username
            skip_parts = 3  # Both /home/username and /Users/username have 3 parts to skip
            path = Path.home().joinpath(*path.parts[skip_parts:])
            assert path.exists(), f"File not found: {path}"
            current_os = "Linux" if platform.system() == "Linux" else "macOS"
            source_os = "Linux" if path.as_posix().startswith("/home") else "macOS"
            console.print(Panel(f"🔗 PATH MAPPING | {source_os} → {current_os}: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
    elif path.as_posix().startswith("C:"):
        if platform.system() in ["Linux", "Darwin"]:  # path copied from Windows to Linux/Mac
            xx = str(a_path).replace("\\\\", "/")
            path = Path.home().joinpath(*Path(xx).parts[3:])  # exclude C:\\Users\\username
            assert path.exists(), f"File not found: {path}"
            target_os = "Linux" if platform.system() == "Linux" else "macOS"
            console.print(Panel(f"🔗 PATH MAPPING | Windows → {target_os}: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
        elif platform.system() == "Windows" and Path.home().as_posix() not in path.as_posix():  # copied from Windows to Windows with different username
            path = Path.home().joinpath(*path.parts[2:])
            assert path.exists(), f"File not found: {path}"
            console.print(Panel(f"🔗 PATH MAPPING | Windows → Windows: `{a_path}` ➡️ `{path}`", title="Path Mapping", expand=False))
    return path.expanduser().absolute()


def find_scripts(root: Path, name_substring: str, suffixes: set[str]) -> tuple[list[Path], list[Path]]:
    filename_matches = []
    partial_path_matches = []
    for entry in root.iterdir():
        if entry.is_dir():
            if entry.name in set(EXCLUDE_DIRS):
                # prune this entire subtree
                continue
            tmp1, tmp2 = find_scripts(entry, name_substring, suffixes)
            filename_matches.extend(tmp1)
            partial_path_matches.extend(tmp2)
        elif entry.is_file() and entry.suffix in suffixes:
            if name_substring.lower() in entry.name.lower():
                filename_matches.append(entry)
            elif name_substring.lower() in entry.as_posix().lower():
                partial_path_matches.append(entry)
    return filename_matches, partial_path_matches


def match_file_name(sub_string: str, search_root: Path, suffixes: set[str]) -> Path:
    search_root_obj = search_root.absolute()
    # assume subscript is filename only, not a sub_path. There is no need to fzf over the paths.
    filename_matches, partial_path_matches = find_scripts(search_root_obj, sub_string, suffixes)
    if len(filename_matches) == 1:
        return Path(filename_matches[0])
    console.print(Panel(f"Partial filename {search_root_obj} match with case-insensitivity failed. This generated #{len(filename_matches)} results.", title="Search", expand=False))
    if len(filename_matches) < 20:
        print("\n".join([a_potential_match.as_posix() for a_potential_match in filename_matches]))
    if len(filename_matches) > 1:
        print(f"Try to narrow down filename_matches search by case-sensitivity, found {len(filename_matches)} results. First @ {filename_matches[0].as_posix()}")
        # let's see if avoiding .lower() helps narrowing down to one result
        reduced_scripts = [a_potential_match for a_potential_match in filename_matches if sub_string in a_potential_match.name]
        if len(reduced_scripts) == 1:
            return Path(reduced_scripts[0])
        elif len(reduced_scripts) > 1:
            from machineconfig.utils.options import choose_from_options
            choice = choose_from_options(multi=False, msg="Multiple matches found", options=reduced_scripts, tv=True)
            return Path(choice)
        print(f"Result: This still generated {len(reduced_scripts)} results.")
        if len(reduced_scripts) < 10:
            print("\n".join([a_potential_match.as_posix() for a_potential_match in reduced_scripts]))

    console.print(Panel(f"Partial path match with case-insensitivity failed. This generated #{len(partial_path_matches)} results.", title="Search", expand=False))
    if len(partial_path_matches) == 1:
        return Path(partial_path_matches[0])
    elif len(partial_path_matches) > 1:
        print("Try to narrow down partial_path_matches search by case-sensitivity.")
        reduced_scripts = [a_potential_match for a_potential_match in partial_path_matches if sub_string in a_potential_match.as_posix()]
        if len(reduced_scripts) == 1:
            return Path(reduced_scripts[0])
        print(f"Result: This still generated {len(reduced_scripts)} results.")        

    try:

        if len(partial_path_matches) == 0:
            print("No partial path matches found, trying to do fd with --no-ignore ...")
            fzf_cmd = f"cd '{search_root_obj}'; fd --no-ignore --type file --strip-cwd-prefix | fzf --ignore-case --exact --query={sub_string}"
        else:
            fzf_cmd = f"cd '{search_root_obj}'; fd --type file --strip-cwd-prefix | fzf --ignore-case --exact --query={sub_string}"
        console.print(Panel(f"🔍 Second attempt: SEARCH STRATEGY | Using fd to search for '{sub_string}' in '{search_root_obj}' ...\n{fzf_cmd}", title="Search Strategy", expand=False))
        search_res_raw = subprocess.run(fzf_cmd, stdout=subprocess.PIPE, text=True, check=True, shell=True).stdout
        search_res = search_res_raw.strip().split("\n")
    except subprocess.CalledProcessError as cpe:
        console.print(Panel(f"❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'.\n{cpe}", title="Error", expand=False))
        import sys
        sys.exit(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results.")
    if len(search_res) == 1:
        return search_root_obj.joinpath(search_res_raw)
    elif len(search_res) == 0:
        msg = Panel(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results", title="File Not Found", expand=False)
        raise FileNotFoundError(msg)

    print(f"⚠️ WARNING | Multiple search results found for `{sub_string}`:\n'{search_res}'")
    cmd = f"cd '{search_root_obj}'; fd --type file | fzf --select-1 --query={sub_string}"
    console.print(Panel(f"🔍 SEARCH STRATEGY | Trying with raw fzf search ...\n{cmd}", title="Search Strategy", expand=False))
    try:
        res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True, shell=True).stdout.strip()
    except subprocess.CalledProcessError as cpe:
        console.print(Panel(f"❌ ERROR | FZF search failed with '{sub_string}' in '{search_root_obj}'. {cpe}", title="Error", expand=False))
        msg = Panel(f"💥 FILE NOT FOUND | Path {sub_string} does not exist @ root {search_root_obj}. No search results", title="File Not Found", expand=False)
        raise FileNotFoundError(msg) from cpe
    return search_root_obj.joinpath(res)


def search_for_files_of_interest(path_obj: Path, suffixes: set[str]) -> list[Path]:
    if path_obj.is_file():
        return [path_obj]
    files: list[Path] = []
    directories_to_visit: list[Path] = [path_obj]
    while directories_to_visit:
        current_dir = directories_to_visit.pop()
        for entry in current_dir.iterdir():
            if entry.is_dir():
                if entry.name == ".venv":
                    continue
                directories_to_visit.append(entry)
                continue
            if entry.suffix not in suffixes:
                continue
            if entry.suffix == ".py" and entry.name == "__init__.py":
                continue
            files.append(entry)
    return files


def get_choice_file(path: str, suffixes: Optional[set[str]]):
    path_obj = sanitize_path(path)
    if suffixes is None:
        import platform
        if platform.system() == "Windows":
            suffixes = {".py", ".ps1", ".sh"}
        elif platform.system() in ["Linux", "Darwin"]:
            suffixes = {".py", ".sh"}
        else:
            suffixes = {".py"}
    if not path_obj.exists():
        print(f"🔍 Searching for file matching `{path}` under `{Path.cwd()}`, but only if suffix matches {suffixes}")
        choice_file = match_file_name(sub_string=path, search_root=Path.cwd(), suffixes=suffixes)
    elif path_obj.is_dir():
        print(f"🔍 Searching recursively for Python, PowerShell and Shell scripts in directory `{path_obj}`")
        files = search_for_files_of_interest(path_obj, suffixes=suffixes)
        print(f"🔍 Got #{len(files)} results.")
        from machineconfig.utils.options import choose_from_options
        choice_file = choose_from_options(multi=False, options=files, tv=True, msg="Choose one option")
        choice_file = Path(choice_file)
    else:
        choice_file = path_obj
    return choice_file
