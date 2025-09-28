ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['number']` in function `_restrict_num_tabs_helper1` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:79:116
   |
79 | ...   return _restrict_num_tabs_helper1(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breakin...
   |                                                                                                              ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['moreLayouts']` in function `_restrict_num_tabs_helper1` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:79:148
   |
79 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['number']` in function `_restrict_num_tabs_helper2` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:81:116
   |
81 | ...   return _restrict_num_tabs_helper2(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breakin...
   |                                                                                                              ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['combineTabs']` in function `_restrict_num_tabs_helper2` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:81:148
   |
81 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['weight']` in function `_restrict_num_tabs_helper3` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:83:116
   |
83 | ...   return _restrict_num_tabs_helper3(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breakin...
   |                                                                                                              ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['moreLayouts']` in function `_restrict_num_tabs_helper3` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:83:148
   |
83 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['weight']` in function `_restrict_num_tabs_helper4` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:85:116
   |
85 | ...   return _restrict_num_tabs_helper4(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breakin...
   |                                                                                                              ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['combineTabs']` in function `_restrict_num_tabs_helper4` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:85:148
   |
85 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:117:33
    |
117 |                 commands.append(f"# Attach to session '{manager.session_name}':")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:118:33
    |
118 |                 commands.append(f"wt -w {manager.session_name}")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_local.py:63:39
   |
63 |                 formatted_args.append(f'"{escaped_arg}"')
   |                                       ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_local.py:65:39
   |
65 |                 formatted_args.append(f'"{arg}"')
   |                                       ^^^^^^^^^^
   |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:177:28
    |
177 |                     info = proc.info
    |                            ^^^^^^^^^
    |
ERROR Missing argument `self` in function `functools._Wrapped.__call__` [missing-argument]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:233:55
    |
233 | ...                   mem = proc_obj.memory_info()
    |                                                 ^^
    |
ERROR Missing required key `pid` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:36
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing required key `name` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:36
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing required key `cmdline` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:36
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing required key `status` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:36
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing required key `pid` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:96
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                                                                                      ^^
    |
ERROR Missing required key `name` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:96
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                                                                                      ^^
    |
ERROR Missing required key `cmdline` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:96
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                                                                                      ^^
    |
ERROR Missing required key `status` for TypedDict `ProcessInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:245:96
    |
245 | ...                   **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
    |                                                                                      ^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_utils/layout_generator.py:60:39
   |
60 |                 formatted_args.append(f'"{escaped_arg}"')
   |                                       ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_utils/layout_generator.py:62:39
   |
62 |                 formatted_args.append(f'"{arg}"')
   |                                       ^^^^^^^^^^
   |
ERROR No attribute `windll` in module `ctypes` [missing-attribute]
  --> src/machineconfig/profile/create.py:73:32
   |
73 |                     is_admin = ctypes.windll.shell32.IsUserAnAdmin()
   |                                ^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/scripts/python/choose_wezterm_theme.py:59:30
   |
59 |             res_lines.append(f"config.color_scheme = '{theme}'")
   |                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/scripts/python/choose_wezterm_theme.py:61:30
   |
61 |             res_lines.append(line)
   |                              ^^^^
   |
ERROR `str` is not assignable to `PathLike[str]` (caused by inconsistent types when breaking cycles) [bad-assignment]
   --> src/machineconfig/scripts/python/helpers/helpers4.py:145:5
    |
145 | /     while path != root_path and trials < 20:
146 | |         for root_file in root_files:
147 | |             if os.path.exists(os.path.join(path, root_file)):
148 | |                 # print(f"Found repo root path: {path}")
149 | |                 return path
150 | |         path = os.path.dirname(path)
    | |_____________________________________^
    |
ERROR Returned type `PathLike[str]` is not assignable to declared return type `str | None` [bad-return]
   --> src/machineconfig/scripts/python/helpers/helpers4.py:149:24
    |
149 |                 return path
    |                        ^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/scripts/python/repos_helper_action.py:139:43
    |
139 |                     failed_remotes.append(f"{remote.name}: {str(e)}")
    |                                           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR `str | None` is not assignable to `None` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/scripts/python/wifi_conn.py:65:13
   |
65 | /             for line in result.stdout.split("\n"):
66 | |                 if "SSID" in line and "BSSID" not in line:
67 | |                     current_ssid = line.split(":")[1].strip()
68 | |                 elif "Signal" in line and current_ssid:
69 | |                     signal = line.split(":")[1].strip()
70 | |                     # Avoid duplicates
   | |_______________________________________^
   |
ERROR Argument `object | str` is not assignable to parameter `exe_name` with type `str` in function `machineconfig.utils.installer_utils.installer_abc.check_if_installed_already` [bad-argument-type]
  --> src/machineconfig/utils/installer.py:41:77
   |
41 |         verdict, current_ver, new_ver = check_if_installed_already(exe_name=exe_name, version=version_to_be_installed, use_cache=False)
   |                                                                             ^^^^^^^^
   |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
  --> src/machineconfig/utils/installer_utils/installer_class.py:48:50
   |
48 |         installer_data_files = InstallerDataFiles(config_data)
   |                                                  ^^^^^^^^^^^^^
   |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
  --> src/machineconfig/utils/installer_utils/installer_class.py:48:51
   |
48 |         installer_data_files = InstallerDataFiles(config_data)
   |                                                   ^^^^^^^^^^^
   |
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
  --> src/machineconfig/utils/options.py:83:43
   |
83 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR `T` is not assignable to `str` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/utils/options.py:86:13
   |
86 |             choice_one: T = default
   |             ^^^^^^^^^^
   |
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
   --> src/machineconfig/utils/options.py:101:47
    |
101 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
    |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
   --> src/machineconfig/utils/options.py:112:47
    |
112 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
    |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
   --> src/machineconfig/utils/options.py:149:31
    |
149 |     return choose_from_options(msg="", options=get_ssh_hosts(), multi=multi, fzf=True)
    |                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR Object of class `str` has no attribute `suffixes` [missing-attribute]
   --> src/machineconfig/utils/path_extended.py:212:41
    |
212 |         full_suffix = suffix or "".join(("bruh" + self).suffixes)
    |                                         ^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `self` in function `functools._Wrapped.__call__` [missing-argument]
  --> src/machineconfig/utils/procs.py:67:52
   |
67 |                     mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
   |                                                    ^^
   |
ERROR Could not import `ProcessManager` from `machineconfig.utils.procs` [missing-module-attribute]
   --> src/machineconfig/utils/procs.py:243:43
    |
243 |     from machineconfig.utils.procs import ProcessManager
    |                                           ^^^^^^^^^^^^^^
    |
