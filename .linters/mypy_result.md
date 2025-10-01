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
src/machineconfig/utils/path_extended.py:497:19: error: Incompatible types in
assignment (expression has type "Any | Iterator[PathExtended]", variable has
type "list[Any]")  [assignment]
                raw = slf.glob(pattern) if not r else self.rglob(pattern)
                      ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/machineconfig/utils/path_extended.py:507:17: error: List comprehension has
incompatible type List[list[PathExtended]]; expected List[Callable[[Any], bool]]
 [misc]
                    PathExtended(comp_file).search(pattern=pattern, r=r, f...
                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_extended.py:512:20: error: Need type annotation
for "haha"  [var-annotated]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/path_extended.py: note: In function "search":
src/machineconfig/utils/path_extended.py:512:40: error: Unsupported left
operand type for + ("Callable[[Any], bool]")  [operator]
                haha = reduce(lambda x, y: x + y, filters_notin) if len(fi...
                                           ^~~~~
src/machineconfig/utils/links.py: note: In function "symlink_map":
src/machineconfig/utils/links.py:121:43: error: Incompatible types (expression
has type "str", TypedDict item "action" has type
"Literal['already_linked', 'relinking', 'fixing_broken_link', 'identical_files', 'backupConfigDefaultPath', 'backing_up_target', 'relink2newSelfManagedPath', 'move2selfManagedPath', 'new_link', 'newLinkAndSelfManagedPath', 'linking', 'error']")
 [typeddict-item]
                            return {"action": action_taken, "details": det...
                                              ^~~~~~~~~~~~
src/machineconfig/utils/links.py:208:27: error: Incompatible types (expression
has type "str", TypedDict item "action" has type
"Literal['already_linked', 'relinking', 'fixing_broken_link', 'identical_files', 'backupConfigDefaultPath', 'backing_up_target', 'relink2newSelfManagedPath', 'move2selfManagedPath', 'new_link', 'newLinkAndSelfManagedPath', 'linking', 'error']")
 [typeddict-item]
            return {"action": action_taken, "details": details}
                              ^~~~~~~~~~~~
src/machineconfig/utils/links.py:213:27: error: Incompatible types (expression
has type "str", TypedDict item "action" has type
"Literal['already_linked', 'relinking', 'fixing_broken_link', 'identical_files', 'backupConfigDefaultPath', 'backing_up_target', 'relink2newSelfManagedPath', 'move2selfManagedPath', 'new_link', 'newLinkAndSelfManagedPath', 'linking', 'error']")
 [typeddict-item]
            return {"action": action_taken, "details": details}
                              ^~~~~~~~~~~~
src/machineconfig/utils/links.py: note: In function "copy_map":
src/machineconfig/utils/links.py:231:43: error: Incompatible types (expression
has type "str", TypedDict item "action" has type
"Literal['already_linked', 'relinking', 'fixing_broken_link', 'identical_files', 'backupConfigDefaultPath', 'backing_up_target', 'relink2newSelfManagedPath', 'move2selfManagedPath', 'new_link', 'newLinkAndSelfManagedPath', 'copying', 'error']")
 [typeddict-item]
                            return {"action": action_taken, "details": det...
                                              ^~~~~~~~~~~~
src/machineconfig/utils/links.py:311:27: error: Incompatible types (expression
has type "str", TypedDict item "action" has type
"Literal['already_linked', 'relinking', 'fixing_broken_link', 'identical_files', 'backupConfigDefaultPath', 'backing_up_target', 'relink2newSelfManagedPath', 'move2selfManagedPath', 'new_link', 'newLinkAndSelfManagedPath', 'copying', 'error']")
 [typeddict-item]
            return {"action": action_taken, "details": details}
                              ^~~~~~~~~~~~
src/machineconfig/utils/links.py:316:27: error: Incompatible types (expression
has type "str", TypedDict item "action" has type
"Literal['already_linked', 'relinking', 'fixing_broken_link', 'identical_files', 'backupConfigDefaultPath', 'backing_up_target', 'relink2newSelfManagedPath', 'move2selfManagedPath', 'new_link', 'newLinkAndSelfManagedPath', 'copying', 'error']")
 [typeddict-item]
            return {"action": action_taken, "details": details}
                              ^~~~~~~~~~~~
src/machineconfig/scripts/python/repos_helper_action.py: note: In function "print_git_operations_summary":
src/machineconfig/scripts/python/repos_helper_action.py:279:9: error: Need type
annotation for "failed_by_action" (hint:
"failed_by_action: dict[<type>, <type>] = ...")  [var-annotated]
            failed_by_action = {}
            ^~~~~~~~~~~~~~~~
src/machineconfig/profile/create.py: note: In function "apply_mapper":
src/machineconfig/profile/create.py:112:24: error: Module has no attribute
"windll"  [attr-defined]
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                           ^~~~~~~~~~~~~
src/machineconfig/cluster/sessions_managers/wt_local_manager.py: note: In member "check_all_sessions_status" of class "WTLocalManager":
src/machineconfig/cluster/sessions_managers/wt_local_manager.py:156:16: error:
Incompatible return value type (got "dict[Any | str, dict[str, Any]]", expected
"dict[str, WTSessionReport]")  [return-value]
            return status_report
                   ^~~~~~~~~~~~~
src/machineconfig/scripts/python/repos_helper_record.py: note: In function "main":
src/machineconfig/scripts/python/repos_helper_record.py:245:56: error: "Path"
has no attribute "rel2home"  [attr-defined]
    ...ve_path = CONFIG_PATH.joinpath("repos").joinpath(repos_root.rel2home()...
                                                        ^~~~~~~~~~~~~~~~~~~
src/machineconfig/utils/options.py: note: In function "choose_from_options":
src/machineconfig/utils/options.py:58:24: error: No overload variant of
"choose_from_options" matches argument types "str", "Iterable[T]", "str", "str",
"str", "T | None", "bool", "bool", "bool"  [call-overload]
                    return choose_from_options(msg=msg, options=options, h...
                           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:58:24: note: Possible overload variants:
src/machineconfig/utils/options.py:58:24: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:58:24: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
src/machineconfig/utils/options.py:76:28: error: No overload variant of
"choose_from_options" matches argument types "str", "Iterable[T]", "str", "str",
"str", "T | None", "bool", "bool", "Literal[False]"  [call-overload]
                        return choose_from_options(msg=msg, options=option...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:76:28: note: Possible overload variants:
src/machineconfig/utils/options.py:76:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:76:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
src/machineconfig/utils/options.py:87:28: error: No overload variant of
"choose_from_options" matches argument types "str", "Iterable[T]", "str", "str",
"str", "T | None", "bool", "bool", "Literal[False]"  [call-overload]
                        return choose_from_options(msg=msg, options=option...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:87:28: note: Possible overload variants:
src/machineconfig/utils/options.py:87:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:87:28: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
src/machineconfig/utils/options.py: note: In function "choose_ssh_host":
src/machineconfig/utils/options.py:124:12: error: No overload variant of
"choose_from_options" matches argument types "str", "list[str]", "bool", "bool" 
[call-overload]
        return choose_from_options(msg="", options=get_ssh_hosts(), multi=...
               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/machineconfig/utils/options.py:124:12: note: Possible overload variants:
src/machineconfig/utils/options.py:124:12: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> T
src/machineconfig/utils/options.py:124:12: note:     def [T] choose_from_options(msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = ..., header: str = ..., tail: str = ..., prompt: str = ..., default: T | None = ..., fzf: bool = ...) -> list[T]
src/machineconfig/utils/files/dbms.py: note: In member "__init__" of class "DBMS":
src/machineconfig/utils/files/dbms.py:48:29: error: Incompatible types in
assignment (expression has type "Path", variable has type "str")  [assignment]
                    path_repr = self.path
                                ^~~~~~~~~
Found 21 errors in 9 files (checked 185 source files)
