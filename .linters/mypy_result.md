src/machineconfig/scripts/python/fire_jobs_args_helper.py: note: In function "extract_kwargs":
src/machineconfig/scripts/python/fire_jobs_args_helper.py:39:9: error: Name
"kwargs" already defined on line 38  [no-redef]
            kwargs: dict[str, object]
            ^~~~~~
src/machineconfig/scripts/python/fire_jobs_args_helper.py:42:31: error:
Incompatible types in assignment (expression has type "bool | None", target has
type "str")  [assignment]
                    kwargs[key] = str2obj[str(value)]
                                  ^~~~~~~~~~~~~~~~~~~
src/machineconfig/scripts/python/fire_jobs_args_helper.py:47:12: error:
Incompatible return value type (got "dict[str, str]", expected
"dict[str, object]")  [return-value]
        return kwargs
               ^~~~~~
src/machineconfig/scripts/python/fire_jobs_args_helper.py:47:12: note: "dict" is invariant -- see https://mypy.readthedocs.io/en/stable/common_issues.html#variance
src/machineconfig/scripts/python/fire_jobs_args_helper.py:47:12: note: Consider using "Mapping" instead, which is covariant in the value type
src/machineconfig/scripts/python/fire_jobs_args_helper.py:47:12: note: Perhaps you need a type annotation for "kwargs"? Suggestion: "dict[str, object]"
src/machineconfig/scripts/python/fire_agents_load_balancer.py: note: In function "chunk_prompts":
src/machineconfig/scripts/python/fire_agents_load_balancer.py:44:9: error: Name
"grouped" already defined on line 33  [no-redef]
            grouped: list[str] = []
            ^~~~~~~
src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py: note: In function "run_monitoring_routine":
src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py:59:17: error:
Need type annotation for "keys" (hint: "keys: list[<type>] = ...") 
[var-annotated]
                    keys = []
                    ^~~~
src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py:62:17: error:
Need type annotation for "values" (hint: "values: list[<type>] = ...") 
[var-annotated]
                    values = []
                    ^~~~~~
src/machineconfig/utils/path_extended.py: note: In member "search" of class "PathExtended":
src/machineconfig/utils/path_extended.py:460:19: error: Incompatible types in
assignment (expression has type "Any | Iterator[PathExtended]", variable has
type "list[Any]")  [assignment]
                raw = slf.glob(pattern) if not r else self.rglob(pattern)
                      ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/machineconfig/utils/path_extended.py:470:17: error: List comprehension has
incompatible type List[list[PathExtended]]; expected List[Callable[[Any], bool]]
 [misc]
                    PathExtended(comp_file).search(pattern=pattern, r=r, f...
                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_extended.py:475:20: error: Need type annotation
for "haha"  [var-annotated]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_extended.py: note: In function "search":
src/machineconfig/utils/path_extended.py:475:40: error: Unsupported left
operand type for + ("Callable[[Any], bool]")  [operator]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                                           ^~~~~
src/machineconfig/utils/installer.py: note: In function "get_all_installer_data_files":
src/machineconfig/utils/installer.py:170:13: error: Name "installer_data"
already defined on line 160  [no-redef]
                installer_data: InstallerData = runpy.run_path(str(item), ...
                ^~~~~~~~~~~~~~
src/machineconfig/scripts/python/devops.py:17:21: error:
"<typing special form>" has no attribute "__args__"  [attr-defined]
    options_list = list(Options.__args__)
                        ^~~~~~~~~~~~~~~~
src/machineconfig/profile/create.py: note: In function "apply_mapper":
src/machineconfig/profile/create.py:73:32: error: Module has no attribute
"windll"  [attr-defined]
                        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                                   ^~~~~~~~~~~~~
src/machineconfig/utils/options.py: note: In function "choose_from_options":
src/machineconfig/utils/options.py:96:24: error: No overload variant of
"choose_from_options" matches argument types "str", "Iterable[T]", "str", "str",
"str", "T | None", "bool", "bool", "bool"  [call-overload]
                    return choose_from_options(msg=msg, options=options, h...
                           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:96:24: note: Possible overload variants:
src/machineconfig/utils/options.py:96:24: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:96:24: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
src/machineconfig/utils/options.py:114:28: error: No overload variant of
"choose_from_options" matches argument types "str", "Iterable[T]", "str", "str",
"str", "T | None", "bool", "bool", "Literal[False]"  [call-overload]
                        return choose_from_options(msg=msg, options=option...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:114:28: note: Possible overload variants:
src/machineconfig/utils/options.py:114:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:114:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
src/machineconfig/utils/options.py:125:28: error: No overload variant of
"choose_from_options" matches argument types "str", "Iterable[T]", "str", "str",
"str", "T | None", "bool", "bool", "Literal[False]"  [call-overload]
                        return choose_from_options(msg=msg, options=option...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:125:28: note: Possible overload variants:
src/machineconfig/utils/options.py:125:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:125:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
src/machineconfig/utils/options.py: note: In function "choose_ssh_host":
src/machineconfig/utils/options.py:162:12: error: No overload variant of
"choose_from_options" matches argument types "str", "list[str]", "bool", "bool" 
[call-overload]
        return choose_from_options(msg="", options=get_ssh_hosts(), multi=...
               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:162:12: note: Possible overload variants:
src/machineconfig/utils/options.py:162:12: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:162:12: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
Found 17 errors in 8 files (checked 181 source files)
