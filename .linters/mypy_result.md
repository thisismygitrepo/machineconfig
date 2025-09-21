src/machineconfig/utils/path_reduced.py: note: In member "search" of class "PathExtended":
src/machineconfig/utils/path_reduced.py:590:19: error: Incompatible types in
assignment (expression has type "Any | Iterator[PathExtended]", variable has
type "list[Any]")  [assignment]
                raw = slf.glob(pattern) if not r else self.rglob(pattern)
                      ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/machineconfig/utils/path_reduced.py:600:17: error: List comprehension has
incompatible type List[list[PathExtended]]; expected List[Callable[[Any], bool]]
 [misc]
                    PathExtended(comp_file).search(pattern=pattern, r=r, f...
                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_reduced.py:605:20: error: Need type annotation for
"haha"  [var-annotated]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_reduced.py: note: In function "search":
src/machineconfig/utils/path_reduced.py:605:40: error: Unsupported left operand
type for + ("Callable[[Any], bool]")  [operator]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                                           ^~~~~
src/machineconfig/utils/notifications.py:17:1: error: Library stubs not
installed for "markdown"  [import-untyped]
    from markdown import markdown
    ^
src/machineconfig/utils/notifications.py:17:1: note: Hint: "python3 -m pip install types-Markdown"
src/machineconfig/utils/notifications.py:17:1: note: (or run "mypy --install-types" to install all missing stub packages)
src/machineconfig/utils/notifications.py:17:1: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
src/machineconfig/utils/code.py: note: In function "write_shell_script_to_default_program_path":
src/machineconfig/utils/code.py:85:73: error: Name "PROGRAM_PATH" is not
defined  [name-defined]
    ...de(code=program, lexer="shell", desc=desc, subtitle=str(PROGRAM_PATH))
                                                               ^~~~~~~~~~~~
src/machineconfig/utils/code.py:86:5: error: Name "PROGRAM_PATH" is not defined
 [name-defined]
        PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
        ^~~~~~~~~~~~
src/machineconfig/utils/code.py:87:5: error: Name "PROGRAM_PATH" is not defined
 [name-defined]
        PROGRAM_PATH.write_text(program, encoding="utf-8")
        ^~~~~~~~~~~~
src/machineconfig/utils/code.py:89:37: error: Name "PROGRAM_PATH" is not
defined  [name-defined]
            result = subprocess.run(f". {PROGRAM_PATH}", shell=True, captu...
                                        ^~~~~~~~~~~~~
src/machineconfig/profile/create.py: note: In function "main_symlinks":
src/machineconfig/profile/create.py:65:32: error: Module has no attribute
"windll"  [attr-defined]
                        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                                   ^~~~~~~~~~~~~
Found 10 errors in 4 files (checked 169 source files)
