# Paths, Files, and Config

This part of the utility API is the filesystem and configuration layer that current Machineconfig code actually uses. The relevant modules today are:

| Module | Role |
| --- | --- |
| `machineconfig.utils.path_core` | Core path operations such as copy, move, delete, symlink, download, temp-path creation, and safe naming |
| `machineconfig.utils.path_helper` | File resolution and interactive path selection helpers |
| `machineconfig.utils.path_reference` | Resolve package-relative asset paths from imported modules |
| `machineconfig.utils.ve` | `.ve.yaml` and `.venv` discovery helpers |
| `machineconfig.utils.io` | JSON / INI / pickle IO plus GPG-backed file encryption helpers |

Older wording around `PathExtended` has been removed here because the current repo centers these modules instead.

---

## `path_core`

`machineconfig.utils.path_core` is the current low-level path toolbox.

Key functions:

| Function | Current behavior |
| --- | --- |
| `resolve()` | Resolve a path with optional non-strict fallback |
| `validate_name()` | Sanitize arbitrary strings for filenames |
| `timestamp()` | Create filename-safe timestamp strings |
| `collapseuser()` | Rewrite a home-prefixed absolute path back to `~` |
| `delete_path()` | Delete a file, symlink, or directory tree |
| `with_name()` | Compute or perform a rename |
| `move()` | Move a file or directory, optionally by `folder`, `name`, or explicit `path` |
| `copy()` | Copy files or directories, with overwrite and `content=True` support |
| `symlink_to()` | Create a symlink, with Windows elevation handling when needed |
| `download()` | Download a URL to a local file, inferring the output filename when possible |
| `tmp()`, `tmpdir()`, `tmpfile()` | Create temp paths under `~/tmp_results` |

Two behaviors worth knowing:

- `copy(..., content=True)` and `move(..., content=True)` act on the children of a directory instead of the directory root itself
- `download()` tries `Content-Disposition`, then the final URL, then the original URL before falling back to a sanitized filename

---

## `path_helper`

`machineconfig.utils.path_helper` is the higher-level file chooser used by commands like `fire` and `croshell`.

Current responsibilities:

- `sanitize_path()` remaps pasted home-directory paths across Linux, macOS, and Windows conventions when needed
- `find_scripts()` and `match_file_name()` search for matching files under a root
- `search_for_files_of_interest()` recursively collects candidate files with suffix filtering
- `get_choice_file()` combines all of that into one path-resolution flow

`get_choice_file()` currently:

- accepts explicit absolute paths directly
- optionally treats relative paths as relative to a provided search root
- defaults suffix filtering by OS when you do not provide one
- recursively searches directories and prompts the user when multiple candidates exist

---

## `path_reference`

`machineconfig.utils.path_reference` is the small bridge between Python modules and package data files.

Use it when a helper module stores shell scripts or other assets next to its Python file:

- `get_path_reference_path(module, path_reference)` returns the absolute path
- `get_path_reference_library_relative_path(module, path_reference)` returns the path relative to `LIBRARY_ROOT`

This is the mechanism used by the current `seek` text-search helpers to load platform-specific shell scripts.

---

## `ve`

`machineconfig.utils.ve` handles the lightweight project metadata that Machineconfig uses to discover environments and cloud defaults.

Key pieces:

- `read_default_cloud_config()` returns the built-in cloud defaults
- `get_ve_path_and_ipython_profile()` walks upward from a path looking for `.ve.yaml`, then falls back to `.venv`
- `get_ve_activate_line()` builds the platform-specific activation command

Current `.ve.yaml` lookup behavior:

- reads `specs.ve_path` when present
- reads `specs.ipy_profile` when present
- falls back to a sibling `.venv`
- stops early once both values are found

---

## `io`

`machineconfig.utils.io` covers the serialization and encryption helpers used by the current codebase.

Main helpers:

| Function or class | Purpose |
| --- | --- |
| `save_json()` / `read_json()` | Persist and read JSON |
| `save_ini()` / `read_ini()` | Persist and read INI files |
| `save_pickle()` / `from_pickle()` | Persist and restore Python objects |
| `remove_c_style_comments()` | Strip `//` and `/* ... */` comments while preserving URLs |
| `encrypt_file_symmetric()` / `decrypt_file_symmetric()` | GPG symmetric encryption using loopback passphrase mode |
| `encrypt_file_asymmetric()` / `decrypt_file_asymmetric()` | GPG public-key encryption and decryption |
| `GpgCommandError` | Rich error wrapper for failed GPG subprocess calls |

Current GPG behavior:

- `build_gpg_environment()` populates `GPG_TTY` when possible
- symmetric helpers stream the password through stdin with `--pinentry-mode loopback`
- asymmetric helpers use `--default-recipient-self`
- `GpgCommandError` includes the command, exit code, stdout, stderr, and a tailored hint when it can infer one

---

## Example usage

```python
from pathlib import Path

from machineconfig.utils.io import read_ini, save_json
from machineconfig.utils.path_core import tmpfile, validate_name
from machineconfig.utils.path_helper import get_choice_file
from machineconfig.utils.ve import get_ve_path_and_ipython_profile

target_path = tmpfile(name=validate_name("example config"), suffix=".json")
save_json({"workers": 8, "queue": "jobs"}, target_path, indent=2)

choice = get_choice_file(path=str(target_path), suffixes={".json"}, search_root=None)
ve_path, ipy_profile = get_ve_path_and_ipython_profile(Path(choice))

print(choice)
print(ve_path, ipy_profile)
print(read_ini(Path("settings.ini")) if Path("settings.ini").exists() else "no ini file")
```

---

## API reference

## Path Core

::: machineconfig.utils.path_core
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Path Helper

::: machineconfig.utils.path_helper
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Path Reference

::: machineconfig.utils.path_reference
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Virtual Environment Helpers

::: machineconfig.utils.ve
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## IO

::: machineconfig.utils.io
    options:
      show_root_heading: true
      show_source: false
      members_order: source
