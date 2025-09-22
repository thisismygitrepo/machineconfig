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
ERROR Missing argument `layout_config` in function `machineconfig.cluster.sessions_managers.wt_local.WTLayoutGenerator.create_wt_layout` [missing-argument]
  --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:38:37
   |
38 |             manager.create_wt_layout(tab_config=tab_config, session_name=full_session_name)
   |                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Unexpected keyword argument `tab_config` in function `machineconfig.cluster.sessions_managers.wt_local.WTLayoutGenerator.create_wt_layout` [unexpected-keyword]
  --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:38:38
   |
38 |             manager.create_wt_layout(tab_config=tab_config, session_name=full_session_name)
   |                                      ^^^^^^^^^^
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
ERROR Object of class `WTLayoutGenerator` has no attribute `tab_config` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:306:81
    |
306 | ...   manager_data = {"session_name": manager.session_name, "tab_config": manager.tab_config, "script_path": manager.script_path}
    |                                                                           ^^^^^^^^^^^^^^^^^^
    |
ERROR Object of class `WTLayoutGenerator` has no attribute `tab_config` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:355:21
    |
355 |                     manager.tab_config = manager_data["tab_config"]
    |                     ^^^^^^^^^^^^^^^^^^
    |
ERROR Object of class `WTLayoutGenerator` has no attribute `tab_config` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:425:131
    |
425 | ...is_active": len(session_windows) > 0, "tab_count": len(manager.tab_config), "tabs": list(manager.tab_config.keys()), "windows": ...
    |                                                           ^^^^^^^^^^^^^^^^^^
    |
ERROR Object of class `WTLayoutGenerator` has no attribute `tab_config` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/wt_local_manager.py:425:165
    |
425 | ... 0, "tab_count": len(manager.tab_config), "tabs": list(manager.tab_config.keys()), "windows": session_windows})
    |                                                           ^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_local.py:61:39
   |
61 |                 formatted_args.append(f'"{escaped_arg}"')
   |                                       ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_local.py:63:39
   |
63 |                 formatted_args.append(f'"{arg}"')
   |                                       ^^^^^^^^^^
   |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:177:24
    |
177 |                     if proc.info["cmdline"] and len(proc.info["cmdline"]) > 0:
    |                        ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:177:53
    |
177 |                     if proc.info["cmdline"] and len(proc.info["cmdline"]) > 0:
    |                                                     ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:179:28
    |
179 | ...   if proc.info["name"] == cmd or cmd in proc.info["cmdline"][0] or any(cmd in arg for arg in proc.info["cmdline"]):
    |          ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:179:63
    |
179 | ...   if proc.info["name"] == cmd or cmd in proc.info["cmdline"][0] or any(cmd in arg for arg in proc.info["cmdline"]):
    |                                             ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:179:116
    |
179 | ...   if proc.info["name"] == cmd or cmd in proc.info["cmdline"][0] or any(cmd in arg for arg in proc.info["cmdline"]):
    |                                                                                                  ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:180:63
    |
180 | ...   matching_processes.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"], "status": pro...
    |                                         ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:180:89
    |
180 | ...   matching_processes.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"], "status": pro...
    |                                                                   ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:180:119
    |
180 | ...   matching_processes.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"], "status": pro...
    |                                                                                                 ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> src/machineconfig/cluster/sessions_managers/zellij_local.py:180:151
    |
180 | ...c.info["name"], "cmdline": proc.info["cmdline"], "status": proc.info["status"]})
    |                                                               ^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/zellij_local_manager.py:163:33
    |
163 |                 commands.append(f"# Attach to session '{manager.session_name}':")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/zellij_local_manager.py:164:33
    |
164 |                 commands.append(f"zellij attach {manager.session_name}")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.layout_generator.LayoutGenerator.create_layout_file` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:56:69
   |
56 |         self.layout_path = self.layout_generator.create_layout_file(layout_config, output_path, self.session_name)
   |                                                                     ^^^^^^^^^^^^^
   |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.layout_generator.LayoutGenerator.generate_layout_content` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:60:62
   |
60 |         return self.layout_generator.generate_layout_content(layout_config)
   |                                                              ^^^^^^^^^^^^^
   |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.process_monitor.ProcessMonitor.check_command_status` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:65:68
   |
65 |         return self.process_monitor.check_command_status(tab_name, self.layout_config, use_verification)
   |                                                                    ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.process_monitor.ProcessMonitor.check_all_commands_status` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:70:63
   |
70 |         return self.process_monitor.check_all_commands_status(self.layout_config)
   |                                                               ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.status_reporter.StatusReporter.get_comprehensive_status` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:78:62
   |
78 |         return self.status_reporter.get_comprehensive_status(self.layout_config)
   |                                                              ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.status_reporter.StatusReporter.print_status_report` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:84:50
   |
84 |         self.status_reporter.print_status_report(self.layout_config)
   |                                                  ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.process_monitor.ProcessMonitor.force_fresh_process_check` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:96:73
   |
96 |         return self.process_monitor.force_fresh_process_check(tab_name, self.layout_config)
   |                                                                         ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `TypedDict[LayoutConfig]` is not assignable to parameter `tab_config` with type `dict[str, tuple[str, str]]` in function `machineconfig.cluster.sessions_managers.zellij_utils.process_monitor.ProcessMonitor.get_verified_process_status` [bad-argument-type]
   --> src/machineconfig/cluster/sessions_managers/zellij_remote.py:104:75
    |
104 |         return self.process_monitor.get_verified_process_status(tab_name, self.layout_config)
    |                                                                           ^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `layout_config` in function `machineconfig.cluster.sessions_managers.zellij_remote.ZellijRemoteLayoutGenerator.create_zellij_layout` [missing-argument]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py:23:38
   |
23 |             an_m.create_zellij_layout(tab_config=tab_config)
   |                                      ^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Unexpected keyword argument `tab_config` in function `machineconfig.cluster.sessions_managers.zellij_remote.ZellijRemoteLayoutGenerator.create_zellij_layout` [unexpected-keyword]
  --> src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py:23:39
   |
23 |             an_m.create_zellij_layout(tab_config=tab_config)
   |                                       ^^^^^^^^^^
   |
ERROR Argument `dict[str, tuple[str, str]]` is not assignable to parameter `layout_config` with type `TypedDict[LayoutConfig]` in function `machineconfig.cluster.sessions_managers.zellij_remote.ZellijRemoteLayoutGenerator.create_zellij_layout` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_utils/example_usage.py:29:54
   |
29 |         layout_path = generator.create_zellij_layout(sample_tabs)
   |                                                      ^^^^^^^^^^^
   |
ERROR Argument `dict[str, tuple[str, str]]` is not assignable to parameter `layout_config` with type `TypedDict[LayoutConfig]` in function `machineconfig.cluster.sessions_managers.zellij_remote.ZellijRemoteLayoutGenerator.get_layout_preview` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_utils/example_usage.py:33:48
   |
33 |         preview = generator.get_layout_preview(sample_tabs)
   |                                                ^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_utils/layout_generator.py:59:39
   |
59 |                 formatted_args.append(f'"{escaped_arg}"')
   |                                       ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> src/machineconfig/cluster/sessions_managers/zellij_utils/layout_generator.py:61:39
   |
61 |                 formatted_args.append(f'"{arg}"')
   |                                       ^^^^^^^^^^
   |
ERROR No attribute `windll` in module `ctypes` [missing-attribute]
  --> src/machineconfig/profile/create.py:74:32
   |
74 |                     is_admin = ctypes.windll.shell32.IsUserAnAdmin()
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
ERROR Type `object` is not iterable [not-iterable]
  --> src/machineconfig/scripts/python/devops_devapps_install.py:41:45
   |
41 |     options = [x.get_description() for x in tqdm(installers, desc="✅ Checking installed programs")] + list(get_args(WHICH_CAT))
   |                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Missing argument `session_layouts` in function `machineconfig.cluster.sessions_managers.zellij_local_manager.ZellijLocalManager.__init__` [missing-argument]
   --> src/machineconfig/scripts/python/fire_agents.py:231:33
    |
231 |     manager = ZellijLocalManager(session2zellij_tabs={"Agents": tab_config}, session_name_prefix=random_name)
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Unexpected keyword argument `session2zellij_tabs` in function `machineconfig.cluster.sessions_managers.zellij_local_manager.ZellijLocalManager.__init__` [unexpected-keyword]
   --> src/machineconfig/scripts/python/fire_agents.py:231:34
    |
231 |     manager = ZellijLocalManager(session2zellij_tabs={"Agents": tab_config}, session_name_prefix=random_name)
    |                                  ^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `layout_config` in function `machineconfig.cluster.sessions_managers.zellij_local.run_zellij_layout` [missing-argument]
   --> src/machineconfig/scripts/python/fire_jobs.py:314:26
    |
314 |         run_zellij_layout(tab_config=tab_config, session_name=None)
    |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Unexpected keyword argument `tab_config` in function `machineconfig.cluster.sessions_managers.zellij_local.run_zellij_layout` [unexpected-keyword]
   --> src/machineconfig/scripts/python/fire_jobs.py:314:27
    |
314 |         run_zellij_layout(tab_config=tab_config, session_name=None)
    |                           ^^^^^^^^^^
    |
ERROR `str` is not assignable to `PathLike[str]` (caused by inconsistent types when breaking cycles) [bad-assignment]
   --> src/machineconfig/scripts/python/helpers/helpers4.py:148:5
    |
148 | /     while path != root_path and trials < 20:
149 | |         for root_file in root_files:
150 | |             if os.path.exists(os.path.join(path, root_file)):
151 | |                 # print(f"Found repo root path: {path}")
152 | |                 return path
153 | |         path = os.path.dirname(path)
    | |_____________________________________^
    |
ERROR Returned type `PathLike[str]` is not assignable to declared return type `str | None` [bad-return]
   --> src/machineconfig/scripts/python/helpers/helpers4.py:152:24
    |
152 |                 return path
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
ERROR No matching overload found for function `dict.__init__` [no-matching-overload]
   --> src/machineconfig/setup_windows/wt_and_pwsh/set_wt_settings.py:125:22
    |
125 |           ubuntu = dict(
    |  ______________________^
126 | |             name="Ubuntu",
127 | |             commandline="wsl -d Ubuntu -- cd ~",
128 | |             hidden=False,
129 | |             guid="{" + str(uuid4()) + "}",
130 | |             startingDirectory="%USERPROFILE%",  # "%USERPROFILE%",   # None: inherent from parent process.
    | |___________________________________________________________________________________________________________^
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
ERROR `T` is not assignable to `str` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/utils/options.py:98:13
   |
98 |             choice_one: T = default
   |             ^^^^^^^^^^
   |
ERROR Object of class `str` has no attribute `suffixes` [missing-attribute]
   --> src/machineconfig/utils/path_reduced.py:212:41
    |
212 |         full_suffix = suffix or "".join(("bruh" + self).suffixes)
    |                                         ^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Could not find import of `win32com.shell.shell` [import-error]
   --> src/machineconfig/utils/path_reduced.py:398:20
    |
398 |             import win32com.shell.shell
    |                    ^^^^^^^^^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Type `object` is not iterable [not-iterable]
  --> src/machineconfig/utils/procs.py:23:17
   |
23 |     for proc in tqdm(psutil.process_iter(), desc="🔎 Scanning processes"):
   |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Type `object` is not iterable [not-iterable]
  --> src/machineconfig/utils/procs.py:56:21
   |
56 |         for proc in tqdm(psutil.process_iter(), desc="🔍 Reading system processes"):
   |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR No matching overload found for function `type.__new__` [no-matching-overload]
   --> src/machineconfig/utils/ssh.py:125:30
    |
125 |         self.tqdm_wrap = type("TqdmWrap", (tqdm,), {"view_bar": view_bar})
    |                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (cls: type[type], o: object, /) -> type [closest match]
  (cls: type[TypeVar[Self]], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwds: Any) -> TypeVar[Self]
ERROR No matching overload found for function `type.__new__` [no-matching-overload]
  --> src/machineconfig/utils/utils2.py:53:17
   |
53 |     inspect(type("TempStruct", (object,), obj)(), value=False, title=title, docs=False, dunder=False, sort=False)
   |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (cls: type[type], o: object, /) -> type [closest match]
  (cls: type[TypeVar[Self]], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwds: Any) -> TypeVar[Self]
