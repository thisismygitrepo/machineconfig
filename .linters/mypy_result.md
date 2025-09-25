src/machineconfig/scripts/python/fire_jobs_args_helper.py: note: In function "extract_kwargs":
src/machineconfig/scripts/python/fire_jobs_args_helper.py:76:9: error: Name
"kwargs" already defined on line 75  [no-redef]
            kwargs: dict[str, object]
            ^~~~~~
src/machineconfig/scripts/python/fire_jobs_args_helper.py:79:31: error:
Incompatible types in assignment (expression has type "bool | None", target has
type "str")  [assignment]
                    kwargs[key] = str2obj[str(value)]
                                  ^~~~~~~~~~~~~~~~~~~
src/machineconfig/scripts/python/fire_jobs_args_helper.py:84:12: error:
Incompatible return value type (got "dict[str, str]", expected
"dict[str, object]")  [return-value]
        return kwargs
               ^~~~~~
src/machineconfig/scripts/python/fire_jobs_args_helper.py:84:12: note: "dict" is invariant -- see https://mypy.readthedocs.io/en/stable/common_issues.html#variance
src/machineconfig/scripts/python/fire_jobs_args_helper.py:84:12: note: Consider using "Mapping" instead, which is covariant in the value type
src/machineconfig/scripts/python/fire_jobs_args_helper.py:84:12: note: Perhaps you need a type annotation for "kwargs"? Suggestion: "dict[str, object]"
src/machineconfig/scripts/python/fire_agents_load_balancer.py: note: In function "chunk_prompts":
src/machineconfig/scripts/python/fire_agents_load_balancer.py:44:9: error: Name
"grouped" already defined on line 33  [no-redef]
            grouped: list[str] = []
            ^~~~~~~
src/machineconfig/utils/path_reduced.py: note: In member "search" of class "PathExtended":
src/machineconfig/utils/path_reduced.py:460:19: error: Incompatible types in
assignment (expression has type "Any | Iterator[PathExtended]", variable has
type "list[Any]")  [assignment]
                raw = slf.glob(pattern) if not r else self.rglob(pattern)
                      ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/machineconfig/utils/path_reduced.py:470:17: error: List comprehension has
incompatible type List[list[PathExtended]]; expected List[Callable[[Any], bool]]
 [misc]
                    PathExtended(comp_file).search(pattern=pattern, r=r, f...
                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_reduced.py:475:20: error: Need type annotation for
"haha"  [var-annotated]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_reduced.py: note: In function "search":
src/machineconfig/utils/path_reduced.py:475:40: error: Unsupported left operand
type for + ("Callable[[Any], bool]")  [operator]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                                           ^~~~~
src/machineconfig/profile/create.py: note: In function "apply_mapper":
src/machineconfig/profile/create.py:73:32: error: Module has no attribute
"windll"  [attr-defined]
                        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                                   ^~~~~~~~~~~~~
Found 9 errors in 4 files (checked 175 source files)
