ERROR `+` is not supported between `tuple[str, ...]` and `Literal['...']` [unsupported-operation]
  --> .ai/tmp_scripts/parser_test/test_integration.py:36:19
   |
36 |             print(sample_block[1][:300] + "...")
   |                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  No matching overload found for function `tuple.__add__`
  Possible overloads:
  (value: tuple[str, ...], /) -> tuple[str, ...] [closest match]
  (value: tuple[_T, ...], /) -> tuple[str | _T, ...]
ERROR Object of class `tuple` has no attribute `replace` [missing-attribute]
  --> .ai/tmp_scripts/test_parse_apps.py:29:99
   |
29 |         preview = group_content.replace('\n', ' ')[:100] + "..." if len(group_content) > 100 else group_content.replace('\n', ' ')
   |                                                                                                   ^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not find import of `machineconfig.scripts.python.devops_devapps_install` [import-error]
  --> .ai/tmp_scripts/test_rich_output.py:10:1
   |
10 | from machineconfig.scripts.python.devops_devapps_install import _handle_installer_not_found, console
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['number']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper1` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:14:115
   |
14 | ...   return restrict_num_tabs_helper1(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking...
   |                                                                                                             ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['moreLayouts']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper1` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:14:147
   |
14 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['number']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper2` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:16:115
   |
16 | ...   return restrict_num_tabs_helper2(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking...
   |                                                                                                             ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['combineTabs']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper2` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:16:147
   |
16 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['weight']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper3` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:18:115
   |
18 | ...   return restrict_num_tabs_helper3(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking...
   |                                                                                                             ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['moreLayouts']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper3` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:18:147
   |
18 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['number', 'weight']` is not assignable to parameter `threshold_type` with type `Literal['weight']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper4` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:20:115
   |
20 | ...   return restrict_num_tabs_helper4(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=threshold_type, breaking...
   |                                                                                                             ^^^^^^^^^^^^^^
   |
ERROR Argument `Literal['combineTabs', 'moreLayouts']` is not assignable to parameter `breaking_method` with type `Literal['combineTabs']` in function `machineconfig.cluster.sessions_managers.utils.load_balancer_helper.restrict_num_tabs_helper4` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/utils/load_balancer.py:20:147
   |
20 | ...x_thresh, threshold_type=threshold_type, breaking_method=breaking_method)
   |                                                             ^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/wt_local.py:147:34
    |
147 |             command_parts.append(" ".join(tab_parts))
    |                                  ^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:128:33
    |
128 |                 commands.append(f"# Attach to session '{manager.session_name}':")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:129:33
    |
129 |                 commands.append(f"wt -w {manager.session_name}")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR `str | None` is not assignable to TypedDict key `session_name` with type `str` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:438:45
    |
438 | ...                   "session_name": session_name,
    |                                       ^^^^^^^^^^^^
    |
ERROR Key `windows` is not defined in TypedDict `ActiveSessionInfo` [typed-dict-key-error]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:442:29
    |
442 | ...                   "windows": session_windows,
    |                       ^^^^^^^^^
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
   --> src/machineconfig/profile/create.py:112:24
    |
112 |             is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    |                        ^^^^^^^^^^^^^
    |
ERROR `Literal['already_linked', 'backing_up_target', 'backupConfigDefaultPath', 'copying', 'error', 'fixing_broken_link', 'identical_files', 'linking', 'move2selfManagedPath', 'newLinkAndSelfManagedPath', 'new_link', 'relink2newSelfManagedPath', 'relinking']` is not assignable to TypedDict key `action` with type `Literal['already_linked', 'backing_up_source', 'backing_up_target', 'copying', 'error', 'fixing_broken_link', 'identical_files', 'linking', 'moving_to_target', 'new_link', 'new_link_and_target', 'relinking', 'relinking_to_new_target']` [typed-dict-key-error]
   --> src/machineconfig/profile/create.py:156:39
    |
156 | ...                   "action": result["action"],
    |                                 ^^^^^^^^^^^^^^^^
    |
ERROR `Literal['already_linked', 'backing_up_target', 'backupConfigDefaultPath', 'copying', 'error', 'fixing_broken_link', 'identical_files', 'linking', 'move2selfManagedPath', 'newLinkAndSelfManagedPath', 'new_link', 'relink2newSelfManagedPath', 'relinking']` is not assignable to TypedDict key `action` with type `Literal['already_linked', 'backing_up_source', 'backing_up_target', 'copying', 'error', 'fixing_broken_link', 'identical_files', 'linking', 'moving_to_target', 'new_link', 'new_link_and_target', 'relinking', 'relinking_to_new_target']` [typed-dict-key-error]
   --> src/machineconfig/profile/create.py:186:35
    |
186 |                         "action": result["action"],
    |                                   ^^^^^^^^^^^^^^^^
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
ERROR Could not find import of `polars` [import-error]
  --> src/machineconfig/scripts/python/count_lines.py:14:12
   |
14 |     import polars as pl
   |            ^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `polars` [import-error]
   --> src/machineconfig/scripts/python/count_lines.py:110:12
    |
110 |     import polars as pl
    |            ^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `plotly.graph_objects` [import-error]
   --> src/machineconfig/scripts/python/count_lines.py:111:12
    |
111 |     import plotly.graph_objects as go
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `polars` [import-error]
   --> src/machineconfig/scripts/python/count_lines.py:187:12
    |
187 |     import polars as pl
    |            ^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `plotly.graph_objects` [import-error]
   --> src/machineconfig/scripts/python/count_lines.py:188:12
    |
188 |     import plotly.graph_objects as go
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `plotly.express` [import-error]
   --> src/machineconfig/scripts/python/count_lines.py:189:12
    |
189 |     import plotly.express as px
    |            ^^^^^^^^^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR `str` is not assignable to `PathLike[str]` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/scripts/python/helpers/helpers4.py:79:5
   |
79 | /     while path != root_path and trials < 20:
80 | |         for root_file in root_files:
81 | |             if os.path.exists(os.path.join(path, root_file)):
82 | |                 # print(f"Found repo root path: {path}")
83 | |                 return path
84 | |         path = os.path.dirname(path)
   | |_____________________________________^
   |
ERROR Returned type `PathLike[str]` is not assignable to declared return type `str | None` [bad-return]
  --> src/machineconfig/scripts/python/helpers/helpers4.py:83:24
   |
83 |                 return path
   |                        ^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/scripts/python/repos_helper_action.py:142:43
    |
142 |                     failed_remotes.append(f"{remote.name}: {str(e)}")
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
ERROR Could not find import of `polars` [import-error]
 --> src/machineconfig/utils/files/dbms.py:4:8
  |
4 | import polars as pl
  |        ^^^^^^^^^^^^
  |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Argument `sqlalchemy.future.engine.Engine | MockConnection` is not assignable to parameter `engine` with type `sqlalchemy.engine.base.Engine` in function `DBMS.__init__` [bad-argument-type]
  --> src/machineconfig/utils/files/dbms.py:68:27
   |
68 | ...engine=cls.make_sql_engine(path=path, echo=echo, share_across_threads=share_across_threads, pool_size=pool_size, **kwargs))
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str | None` is not assignable to parameter `table` with type `str` in function `DBMS._get_table_identifier` [bad-argument-type]
   --> src/machineconfig/utils/files/dbms.py:226:91
    |
226 |                 res = self.con.execute(text(f'''SELECT * FROM {self._get_table_identifier(table, sch)} '''))
    |                                                                                           ^^^^^
    |
ERROR Object of class `NoneType` has no attribute `query` [missing-attribute]
   --> src/machineconfig/utils/files/dbms.py:250:25
    |
250 |                 count = self.ses.query(tbl).count()
    |                         ^^^^^^^^^^^^^^
    |
ERROR No matching overload found for function `dict.__init__` [no-matching-overload]
   --> src/machineconfig/utils/files/dbms.py:265:19
    |
265 |         res = dict(name=table, count=count, size_mb=count * len(tbl.exported_columns) * 10 / 1e6)
    |                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  () -> None
  (**kwargs: _VT) -> None [closest match]
  (map: SupportsKeysAndGetItem[_KT, _VT], /) -> None
  (map: SupportsKeysAndGetItem[str, _VT], /, **kwargs: _VT) -> None
  (iterable: Iterable[tuple[_KT, _VT]], /) -> None
  (iterable: Iterable[tuple[str, _VT]], /, **kwargs: _VT) -> None
  (iterable: Iterable[list[str]], /) -> None
  (iterable: Iterable[list[bytes]], /) -> None
ERROR Could not find import of `matplotlib.pyplot` [import-error]
  --> src/machineconfig/utils/files/read.py:25:24
   |
25 |                 import matplotlib.pyplot as pyplot
   |                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `polars` [import-error]
  --> src/machineconfig/utils/files/read.py:28:24
   |
28 |                 import polars as pl
   |                        ^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `polars` [import-error]
  --> src/machineconfig/utils/files/read.py:31:24
   |
31 |                 import polars as pl
   |                        ^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `numpy` [import-error]
  --> src/machineconfig/utils/files/read.py:70:16
   |
70 |         import numpy as np
   |                ^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `polars` [import-error]
  --> src/machineconfig/utils/files/read.py:97:16
   |
97 |         import polars as pl
   |                ^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Argument `object | str` is not assignable to parameter `exe_name` with type `str` in function `machineconfig.utils.installer_utils.installer_abc.check_if_installed_already` [bad-argument-type]
  --> src/machineconfig/utils/installer.py:43:77
   |
43 |         verdict, current_ver, new_ver = check_if_installed_already(exe_name=exe_name, version=version_to_be_installed, use_cache=False)
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
  --> src/machineconfig/utils/options.py:58:43
   |
58 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR `T` is not assignable to `str` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/utils/options.py:61:13
   |
61 |             choice_one: T = default
   |             ^^^^^^^^^^
   |
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
  --> src/machineconfig/utils/options.py:76:47
   |
76 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
  --> src/machineconfig/utils/options.py:87:47
   |
87 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
   --> src/machineconfig/utils/options.py:124:31
    |
124 |     return choose_from_options(msg="", options=get_ssh_hosts(), multi=multi, fzf=True)
    |                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR Object of class `str` has no attribute `suffixes` [missing-attribute]
   --> src/machineconfig/utils/path_extended.py:251:41
    |
251 |         full_suffix = suffix or "".join(("bruh" + self).suffixes)
    |                                         ^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR `tmp` may be uninitialized [unbound-name]
   --> src/machineconfig/utils/path_extended.py:390:42
    |
390 |         return round(number=total_size / tmp, ndigits=1)
    |                                          ^^^
    |
ERROR Missing argument `self` in function `functools._Wrapped.__call__` [missing-argument]
  --> src/machineconfig/utils/procs.py:65:52
   |
65 |                     mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
   |                                                    ^^
   |
ERROR Could not import `ProcessManager` from `machineconfig.utils.procs` [missing-module-attribute]
   --> src/machineconfig/utils/procs.py:240:43
    |
240 |     from machineconfig.utils.procs import ProcessManager
    |                                           ^^^^^^^^^^^^^^
    |
