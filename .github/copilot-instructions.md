
---
applyTo: "**/*.py"
---

# Python Development Environment and tooling:
* If you find that uv is not available in terminal, look for how to install it in https://github.com/astral-sh/uv
* To initialize a new python project, use `cd $repo_root; uv init --python 3.13`
* To create virtual env, use `cd $repo_root; uv venv`.
* To install venv and dependency of an existing project, use `cd $repo_root; uv sync`.
* Please run any python file using `uv run $file.py`
* Same for tools, e.g. `un run python pytest $file_path`
* To add a package, use `cd $repo_root; uv add <package_name>`.
    * Please never mention versions of package, so uv will bring the latest.
    * On this note, I have to say that I am seriously concerned about AI using very outdated coding style.
        * Use python 3.13 syntax features.
        * Use modern standards, e.g. Path from pathlib.
* Never touch `pyproject.toml` manually, this file is strictly managed by `uv` tool on your behalf.
* If you are writing a test or any temporary script for discovering or undestanding something as an intermediate step, then,
  please keep all your temp scripts and files under ./.ai/tmp_scripts directory, its included in .gitignore and won't litter the repo.
  Its also nice if you create a subdirectory therein to contain relevant files for the task at hand, to avoid confusion with other files from other ai agents working simulataneously on other things.
* When you run a command in the terminal, please don't assume that it will run in the correct repo root directory. Always cd first to the repo root, or the desired directory, then run the command.

# Python Coding Rules
* Please type hint all the code. Use fully quilaified types, not just generics like dict, list, etc, rather dict[str, int], list[float], 'npt.NDarray[np.float32]', etc.
* Use `Any` type only if absoloutely necessary.
* Please use `# type: ignore blah blah`, to silence any warning from pyright or other linters and type checkers, but only when necessary. Otherwise, listen to them and adjust accordingly, or use cast from typing.
* Use typeddict, dataclasses and literals when necessary to avoid blackbox str or dict[str, str] etc.
* ALL functions / methods etc must clearly indicate the return type.
* Do not leave dangling imports or variables unused, prefix their name with underscore if necessary to undicate they are unused.
* Please prefer to use absolute imports, avoid relatives when possible.
* Use triple quotes and triple double quotes f-strings for string formatting and avoid when possible all goofy escaping when interpolation.
* If needed, opt for polars not pandas, whenever possible.
* when finished, run a linting static analysis check against files you touched, Any fix any mistakes.
* Please run `uv run -m pyright $file_touched` and address all issues. if `pyright is not there, first run `uv add pyright --dev`.
* For all type checkers and linters, like mypy, pyright, pyrefly and pylint, there are config files at different levels of the repo all the way up to home directory level. You don't need to worry about them, just be mindful that they exist. The tools themselves will respect the configs therein.
* If you want to run all linters and pycheckers agains the entire project to make sure everything is clean, I prepared a nice shell script, you can run it from the repo root as `./.ai/scripts/lint_and_type_check.sh`. It will produce markdown files that are you are meant to look at @ ./.ai/linters/*.md
* Rust-inspired style, e.g.
from typing import Literal, Optional, TypeAlias
class Success:
  def __init__(self, value: int):
    self.value = value
FAILURE_REASON: TypeAlias = Literal["cache_missing", "service_history_missing"]
class Failure:
    def __init__(self, reason: FAILURE_REASON, message: Optional[str] = None):
        self.reason: FAILURE_REASON = reason
        self.message = message
def fallible_function(a: int, b: int) -> Success | Failure:
    if a > b: return Success(value=a+b)
    else: return Failure(reason="service_history_missing", message="a is not greater than b")
def example_usage() -> None:
    result = fallible_function(2, 3)
    match result:
        case Success():  # Correct
            print("Addition succeeded.")
        case Failure():  # <--- Looks wrong, because no variable passed, but its correct, it works like this in python3.11+
            # Now this only matches if result IS a Failure instance
            print("Addition failed.")
            print(f"Reason: {result.reason}, Message: {result.message}")
            q = result.reason
            match q:
                case "cache_missing":
                    print("Handle cache missing scenario.")
                case "service_history_missing":
                    print("Handle service history missing scenario.")


# General Programming Ethos:
* Make sure all the code is rigorous, no lazy stuff.
    * For example, always avoid default values in arguments of functions. Those are evil and cause confusion. Always be explicit in parameter passing.
    * Please never ever attempt to change code files by writing meta code to do string manipulation on files, e.g. with `sed` command with terminal. Please do change the files one by one, no matter how many there is. Don't worry about time, nor context window size, its okay, take your time and do the legwork. You can stop in the middle and we will have another LLM to help with the rest.
* Your code is minimal, no unrequested features, no bloat.
* Please avoid writing README files and avoid docstring and comments in code unless absolutely necessary. Use clear naming conventions instead of documenting.
* Always prefer to functional style of programming over OOP.
* When passing arguments or constructing dicts or lists or tuples, avoid breaking lines too much, try to use ~ 150 characters per line before breaking to new one.

# Privacy:
* No matter what, never ever open/read/write/list anything under ~/dotfiles
