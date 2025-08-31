

Hello
=====


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
* Please type hint all the code. Use fully quilaified types, not just generics like dict, list, etc, rather dict[str, int], list[float], etc.
* Use triple quotes and triple double quotes f-strings for string formatting and avoid when possible all goofy escaping when interpolation.
* Make sure all the code is rigorous, no lazy stuff.
    * For example, always avoid default values in arguments of functions. Those are evil and cause confusion. Always be explicit
* Please avoid writing READMe files and avoid docstring and comments in code unless absolutely necessary. Use clear naming conventions instead of documenting.

# Preferences:
* If needed, opt for polars not pandas, whenever possible.
