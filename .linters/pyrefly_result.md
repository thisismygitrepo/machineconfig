ERROR Could not find import of `typer` [import-error]
  --> .ai/tmp_scripts/argparse_typing_examples/approach3_modern_libs.py:15:16
   |
15 |         import typer
   |                ^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `click` [import-error]
  --> .ai/tmp_scripts/argparse_typing_examples/approach3_modern_libs.py:80:16
   |
80 |         import click
   |                ^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `pydantic` [import-error]
   --> .ai/tmp_scripts/argparse_typing_examples/approach3_modern_libs.py:127:9
    |
127 |         from pydantic import BaseModel, Field
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not import `_search_python_files` from `machineconfig.scripts.python.fire_agents` [missing-module-attribute]
  --> .ai/tmp_scripts/test_fire_agents.py:10:54
   |
10 | from machineconfig.scripts.python.fire_agents import _search_python_files, _search_files_by_pattern
   |                                                      ^^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `_search_files_by_pattern` from `machineconfig.scripts.python.fire_agents` [missing-module-attribute]
  --> .ai/tmp_scripts/test_fire_agents.py:10:76
   |
10 | from machineconfig.scripts.python.fire_agents import _search_python_files, _search_files_by_pattern
   |                                                                            ^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `dict[str, tuple[str, str]]` is not assignable to parameter `tabs` with type `list[TypedDict[TabConfig]]` in function `machineconfig.cluster.sessions_managers.wt_utils.layout_generator.WTLayoutGenerator.create_wt_script` [bad-argument-type]
  --> .ai/tmp_scripts/test_layout_generator_ps1.py:24:46
   |
24 |     script_path = generator.create_wt_script(test_config, output_dir, "TestLayoutGen")
   |                                              ^^^^^^^^^^^
   |
ERROR Could not find import of `machineconfig.cluster.sessions_managers.layout_types` [import-error]
  --> .ai/tmp_scripts/test_ps1_changes.py:10:1
   |
10 | from machineconfig.cluster.sessions_managers.layout_types import LayoutConfig
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Missing argument `output_dir` in function `machineconfig.cluster.sessions_managers.wt_local.WTLayoutGenerator.create_wt_layout` [missing-argument]
  --> .ai/tmp_scripts/test_ps1_changes.py:25:45
   |
25 |     script_path = generator.create_wt_layout(test_layout)
   |                                             ^^^^^^^^^^^^^
   |
ERROR Could not import `P` from `machineconfig.utils.path_reduced` [missing-module-attribute]
  --> .ai/tmp_scripts/test_repr_inline.py:10:46
   |
10 | from machineconfig.utils.path_reduced import P
   |                                              ^
   |
ERROR Could not import `P` from `machineconfig.utils.path_reduced` [missing-module-attribute]
  --> .ai/tmp_scripts/test_time_deprecation.py:11:46
   |
11 | from machineconfig.utils.path_reduced import P
   |                                              ^
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
ERROR Could not find name `get_all_dicts` [unknown-name]
  --> src/machineconfig/scripts/python/devops_devapps_install.py:45:74
   |
45 |     installers = [Installer.from_dict(d=vd, name=name) for __kat, vds in get_all_dicts(system=system()).items() for name, vd in vds....
   |                                                                          ^^^^^^^^^^^^^
   |
ERROR Object of class `NoneType` has no attribute `lower` [missing-attribute]
  --> src/machineconfig/scripts/python/fire_jobs_layout_helper.py:27:110
   |
27 | ...   layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"].lower() == layout_name.lower()), None)
   |                                                                                                            ^^^^^^^^^^^^^^^^^
   |
ERROR `str` is not assignable to `PathLike[str]` (caused by inconsistent types when breaking cycles) [bad-assignment]
   --> src/machineconfig/scripts/python/helpers/helpers4.py:147:5
    |
147 | /     while path != root_path and trials < 20:
148 | |         for root_file in root_files:
149 | |             if os.path.exists(os.path.join(path, root_file)):
150 | |                 # print(f"Found repo root path: {path}")
151 | |                 return path
152 | |         path = os.path.dirname(path)
    | |_____________________________________^
    |
ERROR Returned type `PathLike[str]` is not assignable to declared return type `str | None` [bad-return]
   --> src/machineconfig/scripts/python/helpers/helpers4.py:151:24
    |
151 |                 return path
    |                        ^^^^
    |
ERROR `str | None` is not assignable to `None` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/scripts/python/wifi_conn.py:64:13
   |
64 | /             for line in result.stdout.split("\n"):
65 | |                 if "SSID" in line and "BSSID" not in line:
66 | |                     current_ssid = line.split(":")[1].strip()
67 | |                 elif "Signal" in line and current_ssid:
68 | |                     signal = line.split(":")[1].strip()
69 | |                     # Avoid duplicates
   | |_______________________________________^
   |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:132:50
    |
132 |     res_final["OS_SPECIFIC"] = InstallerDataFiles(os_specific_data)
    |                                                  ^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:132:51
    |
132 |     res_final["OS_SPECIFIC"] = InstallerDataFiles(os_specific_data)
    |                                                   ^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:136:49
    |
136 |     res_final["OS_GENERIC"] = InstallerDataFiles(os_generic_data)
    |                                                 ^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:136:50
    |
136 |     res_final["OS_GENERIC"] = InstallerDataFiles(os_generic_data)
    |                                                  ^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:140:54
    |
140 |     res_final["OS_SPECIFIC_DEV"] = InstallerDataFiles(os_specific_dev_data)
    |                                                      ^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:140:55
    |
140 |     res_final["OS_SPECIFIC_DEV"] = InstallerDataFiles(os_specific_dev_data)
    |                                                       ^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:144:53
    |
144 |     res_final["OS_GENERIC_DEV"] = InstallerDataFiles(os_generic_dev_data)
    |                                                     ^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:144:54
    |
144 |     res_final["OS_GENERIC_DEV"] = InstallerDataFiles(os_generic_dev_data)
    |                                                      ^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `repoURL` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:158:43
    |
158 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `doc` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:158:43
    |
158 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `filenameTemplate` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:158:43
    |
158 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `stripVersion` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:158:43
    |
158 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `exeName` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:158:43
    |
158 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Expected argument `appName` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:158:44
    |
158 |             installer_data = InstallerData(config_dict)
    |                                            ^^^^^^^^^^^
    |
ERROR Missing argument `repoURL` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:170:43
    |
170 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `doc` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:170:43
    |
170 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `filenameTemplate` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:170:43
    |
170 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `stripVersion` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:170:43
    |
170 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Missing argument `exeName` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:170:43
    |
170 |             installer_data = InstallerData(config_dict)
    |                                           ^^^^^^^^^^^^^
    |
ERROR Expected argument `appName` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:170:44
    |
170 |             installer_data = InstallerData(config_dict)
    |                                            ^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:175:45
    |
175 |     res_final["CUSTOM"] = InstallerDataFiles({"version": "1", "installers": res_custom_installers})
    |                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:175:46
    |
175 |     res_final["CUSTOM"] = InstallerDataFiles({"version": "1", "installers": res_custom_installers})
    |                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:176:49
    |
176 |     res_final["CUSTOM_DEV"] = InstallerDataFiles({"version": "1", "installers": res_custom_dev_installers})
    |                                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:176:50
    |
176 |     res_final["CUSTOM_DEV"] = InstallerDataFiles({"version": "1", "installers": res_custom_dev_installers})
    |                                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer_utils/installer_class.py:102:50
    |
102 |         installer_data_files = InstallerDataFiles(config_data)
    |                                                  ^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer_utils/installer_class.py:102:51
    |
102 |         installer_data_files = InstallerDataFiles(config_data)
    |                                                   ^^^^^^^^^^^
    |
ERROR `T` is not assignable to `str` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/utils/options.py:96:13
   |
96 |             choice_one: T = default
   |             ^^^^^^^^^^
   |
ERROR Object of class `str` has no attribute `suffixes` [missing-attribute]
   --> src/machineconfig/utils/path_reduced.py:212:41
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
ERROR No matching overload found for function `type.__new__` [no-matching-overload]
  --> src/machineconfig/utils/utils2.py:67:17
   |
67 |     inspect(type("TempStruct", (object,), obj)(), value=False, title=title, docs=False, dunder=False, sort=False)
   |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (cls: type[type], o: object, /) -> type [closest match]
  (cls: type[TypeVar[Self]], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwds: Any) -> TypeVar[Self]
