
# Development Environment and tooling:
* To initialize a python project, use `uv init --python 3.13`
* To create virtual env, use `uv venv`.
* Please run any python file using `uv run $file.py`
* Same for tools, e.g. `un run python pytest blah`
* To add a package, use `uv add <package_name>`.
    * Please never mention versions of package, so uv will bring the latest.
    * On this note, I have to say that I am seriously concerned about AI using very outdated coding style.
        * Use python 3.13 syntax features.
        * Use modern standards, e.g. Path from pathlib.

* Never touch `pyproject.toml` manually, this file is strictly managed by `uv` tool on your behalf.
* If you are writing a test or any temporary script for discovering or undestanding something as an intermediate step, then,
  please keep all your temp scripts and files under ./.ai/tmp_scripts directory, its included in .gitignore and won't litter the repo.
  Its also nice if you create a subdirectory therein to contain relevant files for the task at hand, to avoid confusion with other files from other ai agents working simulataneously on other things.

# Style
* Please type hint all the code. Use fully quilaified types, not just generics like dict, list, etc, rather dict[str, int], list[float], 'npt.NDarray[np.float32]', etc.
* Use `Any` type only if absoloutely necessary.
* Please use `# type: ignore blah blah`, to silence any warning from pyright or other linters and type checkers, but only when necessary. Otherwise, listen to them and adjust accordingly, or use cast from typing.
* Use typeddict, dataclasses and literals when necessary to avoid blackbox str or dict[str, str] etc.
* ALL functions / methods etc must clearly indicate the return type.
* Do not leave dangling imports or variables unused, prefix their name with underscore if necessary to undicate they are unused.
* Use triple quotes and triple double quotes f-strings for string formatting and avoid when possible all goofy escaping when interpolation.
* Make sure all the code is rigorous, no lazy stuff.
    * For example, always avoid default values in arguments of functions. Those are evil and cause confusion. Always be explicit in parameter passing.
* Please prefer to use absolute imports, avoid relatives when possible.
* Please avoid writing README files and avoid docstring and comments in code unless absolutely necessary. Use clear naming conventions instead of documenting.
* Always prefer to functional style of programming over OOP.
* If needed, opt for polars not pandas, whenever possible.
* When passing arguments or constructing dicts or lists or tuples, avoid breaking lines too much, try to use ~ 150 characters per line before breaking to new one.
* when finished, run a linting static analysis check against files you touched, any fix any mistakes.
* Please run `uv run -m pyright $file_touched` and address all issues. if `pyright is not there, first run `uv add pyright --dev`.
