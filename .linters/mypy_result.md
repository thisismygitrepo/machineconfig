src/machineconfig/scripts/python/mount_nw_drive.py: note: In function "main":
src/machineconfig/scripts/python/mount_nw_drive.py:15:23: error: Incompatible
types in assignment (expression has type "Path", variable has type "str") 
[assignment]
            mount_point = Path.home().joinpath(fr"data/mount_nw/{machine_n...
                          ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/scripts/python/mount_nw_drive.py:17:23: error: Incompatible
types in assignment (expression has type "Path", variable has type "str") 
[assignment]
            mount_point = Path(mount_point).expanduser()
                          ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/machineconfig/jobs/python_custom_installers/dev/winget.py:2:1: error:
Library stubs not installed for "requests"  [import-untyped]
    import requests
    ^
src/machineconfig/jobs/python_custom_installers/dev/winget.py:2:1: note: Hint: "python3 -m pip install types-requests"
src/machineconfig/jobs/python_custom_installers/dev/winget.py:2:1: note: (or run "mypy --install-types" to install all missing stub packages)
src/machineconfig/jobs/python_custom_installers/dev/winget.py:2:1: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
src/machineconfig/utils/io_save.py:8:1: error: Library stubs not installed for
"toml"  [import-untyped]
    import toml
    ^
src/machineconfig/utils/io_save.py:8:1: note: Hint: "python3 -m pip install types-toml"
src/machineconfig/utils/io_save.py:9:1: error: Library stubs not installed for
"yaml"  [import-untyped]
    import yaml
    ^
src/machineconfig/utils/io_save.py:9:1: note: Hint: "python3 -m pip install types-PyYAML"
src/machineconfig/utils/cloud/onedrive/transaction.py:39:1: error: Library
stubs not installed for "requests"  [import-untyped]
    import requests
    ^
src/machineconfig/utils/path_reduced.py:130:1: error: Library stubs not
installed for "requests"  [import-untyped]
            import requests
    ^
src/machineconfig/utils/path_reduced.py: note: In member "symlink_to" of class "P":
src/machineconfig/utils/path_reduced.py:268:5: error: Signature of "symlink_to"
incompatible with supertype "pathlib.Path"  [override]
        def symlink_to(self, target: PLike, verbose: bool = True, overwrit...
        ^
src/machineconfig/utils/path_reduced.py:268:5: note: Error code "override" not covered by "type: ignore" comment
src/machineconfig/utils/path_reduced.py:268:5: note:      Superclass:
src/machineconfig/utils/path_reduced.py:268:5: note:          def symlink_to(self, target: str | bytes | PathLike[str] | PathLike[bytes], target_is_directory: bool = ...) -> None
src/machineconfig/utils/path_reduced.py:268:5: note:      Subclass:
src/machineconfig/utils/path_reduced.py:268:5: note:          def symlink_to(self, target: str | P | Path, verbose: bool = ..., overwrite: bool = ..., orig: bool = ..., strict: bool = ...) -> Any
src/machineconfig/utils/path_reduced.py: note: In member "unzip" of class "P":
src/machineconfig/utils/path_reduced.py:368:45: error: Item "str" of
"str | Any | Path" has no attribute "parent"  [union-attr]
            folder = folder if not content else folder.parent
                                                ^~~~~~~~~~~~~
src/machineconfig/utils/path_reduced.py: note: In member "_resolve_path" of class "P":
src/machineconfig/utils/path_reduced.py:439:24: error: Item "str" of
"str | Any | Path" has no attribute "is_dir"  [union-attr]
                assert not path.is_dir(), f"`path` passed is a directory! ...
                           ^~~~~~~~~~~
src/machineconfig/utils/path_reduced.py:440:20: error: Incompatible return
value type (got "str | Any | Path", expected "P")  [return-value]
                return path
                       ^~~~
src/machineconfig/utils/procs.py:5:1: error: Library stubs not installed for
"pytz"  [import-untyped]
    from pytz import timezone
    ^
src/machineconfig/utils/procs.py:5:1: note: Hint: "python3 -m pip install types-pytz"
src/machineconfig/utils/options.py:145:1: error: Library stubs not installed
for "paramiko"  [import-untyped]
        from paramiko import SSHConfig
    ^
src/machineconfig/utils/options.py:145:1: note: Hint: "python3 -m pip install types-paramiko"
src/machineconfig/utils/installer.py: note: In function "check_latest":
src/machineconfig/utils/installer.py:58:5: error: Need type annotation for
"grouped_data" (hint: "grouped_data: dict[<type>, <type>] = ...") 
[var-annotated]
        grouped_data = {}
        ^~~~~~~~~~~~
src/machineconfig/utils/installer_utils/installer_class.py:220:1: error:
Library stubs not installed for "requests"  [import-untyped]
                import requests  # https://docs.github.com/en/repositories...
    ^
Found 15 errors in 9 files (checked 165 source files)
