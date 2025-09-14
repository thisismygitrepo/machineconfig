src/machineconfig/scripts/python/ai/generate_files.py: note: In function "main":
src/machineconfig/scripts/python/ai/generate_files.py:69:5: error: Name
"repo_root" already defined on line 43  [no-redef]
        repo_root: str = str(pathlib.Path.cwd().resolve())
        ^~~~~~~~~
src/machineconfig/utils/path_reduced.py: note: In member "search" of class "P":
src/machineconfig/utils/path_reduced.py:581:19: error: Incompatible types in
assignment (expression has type "Any | Iterator[P]", variable has type
"list[Any]")  [assignment]
                raw = slf.glob(pattern) if not r else self.rglob(pattern)
                      ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/machineconfig/utils/path_reduced.py:590:30: error: List comprehension has
incompatible type List[list[P]]; expected List[Callable[[Any], bool]]  [misc]
                filters_notin = [P(comp_file).search(pattern=pattern, r=r,...
                                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_reduced.py:594:20: error: Need type annotation for
"haha"  [var-annotated]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_reduced.py: note: In function "search":
src/machineconfig/utils/path_reduced.py:594:40: error: Unsupported left operand
type for + ("Callable[[Any], bool]")  [operator]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                                           ^~~~~
src/machineconfig/profile/create.py: note: In function "main_symlinks":
src/machineconfig/profile/create.py:65:32: error: Module has no attribute
"windll"  [attr-defined]
                        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                                   ^~~~~~~~~~~~~
Found 6 errors in 3 files (checked 169 source files)
