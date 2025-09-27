ERROR Parse error: missing closing quote in string literal [parse-error]
  --> .ai/tmp_prompts/AI_Agents_K3dtsb6BoD/aa_agents_relaunch.py:21:13
   |
21 | separator = "
   |             ^
   |
ERROR Parse error: Expected a statement [parse-error]
  --> .ai/tmp_prompts/AI_Agents_K3dtsb6BoD/aa_agents_relaunch.py:21:14
   |
21 | separator = "
   |              ^
22 | "
   |
ERROR Parse error: missing closing quote in string literal [parse-error]
  --> .ai/tmp_prompts/AI_Agents_K3dtsb6BoD/aa_agents_relaunch.py:22:1
   |
22 | "
   | ^
   |
ERROR Parse error: Expected a statement [parse-error]
  --> .ai/tmp_prompts/AI_Agents_K3dtsb6BoD/aa_agents_relaunch.py:22:2
   |
22 | "
   |  ^
23 | prompt_material_path = Path("/home/alex/code/machineconfig/.ai/target_file.txt")
   |
ERROR Could not find name `regenerate_py_code` [unknown-name]
  --> .ai/tmp_prompts/AI_Agents_K3dtsb6BoD/aa_agents_relaunch.py:31:56
   |
31 | (agents_dir / "aa_agents_relaunch.py").write_text(data=regenerate_py_code, encoding="utf-8")
   |                                                        ^^^^^^^^^^^^^^^^^^
   |
ERROR TypedDict `LayoutsFile` does not have key `layoutTabs` [typed-dict-key-error]
  --> .ai/tmp_prompts/AI_Agents_K3dtsb6BoD/aa_agents_relaunch.py:34:15
   |
34 | if len(layout["layoutTabs"]) > 25:
   |               ^^^^^^^^^^^^
   |
ERROR Could not find name `ZellijLocalManager` [unknown-name]
  --> .ai/tmp_prompts/AI_Agents_K3dtsb6BoD/aa_agents_relaunch.py:37:11
   |
37 | manager = ZellijLocalManager(session_layouts=[layout])
   |           ^^^^^^^^^^^^^^^^^^
   |
ERROR Could not find import of `pydantic` [import-error]
   --> .ai/tmp_scripts/argparse_typing_examples/approach3_modern_libs.py:127:9
    |
127 |         from pydantic import BaseModel, Field
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `src.machineconfig.utils.github_release_parser` [import-error]
  --> .ai/tmp_scripts/github_download_example.py:16:1
   |
16 | from src.machineconfig.utils.github_release_parser import get_github_download_link
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `machineconfig.utils.path_reduced` [import-error]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:13:1
   |
13 | from machineconfig.utils.path_reduced import PathExtended
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `machineconfig.utils.utils2` [import-error]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:24:5
   |
24 |     from machineconfig.utils.utils2 import read_json
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:28:46
   |
28 |     installer_data_files = InstallerDataFiles(config_data)
   |                                              ^^^^^^^^^^^^^
   |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:28:47
   |
28 |     installer_data_files = InstallerDataFiles(config_data)
   |                                               ^^^^^^^^^^^
   |
ERROR Missing argument `doc` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:35:35
   |
35 |     installer_data = InstallerData(first_installer)
   |                                   ^^^^^^^^^^^^^^^^^
   |
ERROR Missing argument `repoURL` in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [missing-argument]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:35:35
   |
35 |     installer_data = InstallerData(first_installer)
   |                                   ^^^^^^^^^^^^^^^^^
   |
ERROR Expected argument `appName` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerData.__init__` [unexpected-positional-argument]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:35:36
   |
35 |     installer_data = InstallerData(first_installer)
   |                                    ^^^^^^^^^^^^^^^
   |
ERROR TypedDict `InstallerData` does not have key `exeName` [typed-dict-key-error]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:36:77
   |
36 |     print(f"✅ First installer: {installer_data['appName']} ({installer_data['exeName']})")
   |                                                                              ^^^^^^^^^
   |
ERROR Class `Installer` has no class attribute `from_installer_data` [missing-attribute]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:49:17
   |
49 |     installer = Installer.from_installer_data(installer_data=first_installer_data)
   |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Object of class `Installer` has no attribute `exe_name` [missing-attribute]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:84:22
   |
84 |         print(f"  - {installer.exe_name}: {installer.doc[:50]}...")
   |                      ^^^^^^^^^^^^^^^^^^
   |
ERROR Object of class `Installer` has no attribute `doc` [missing-attribute]
  --> .ai/tmp_scripts/installer_refactor/test_new_installer_types.py:84:44
   |
84 |         print(f"  - {installer.exe_name}: {installer.doc[:50]}...")
   |                                            ^^^^^^^^^^^^^
   |
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
ERROR Could not find import of `src.machineconfig.utils.github_release_parser` [import-error]
  --> .ai/tmp_scripts/test_github_parser.py:10:1
   |
10 | from src.machineconfig.utils.github_release_parser import get_download_link, get_github_download_link
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `src.machineconfig.utils.github_installer_generator` [import-error]
  --> .ai/tmp_scripts/test_installer_generator.py:11:1
   |
11 | from src.machineconfig.utils.github_installer_generator import generate_installer_data_from_github
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Unexpected keyword argument `kw` in function `machineconfig.scripts.python.fire_jobs_args_helper.FireJobArgs.__init__` [unexpected-keyword]
  --> .ai/tmp_scripts/test_kw_format.py:10:24
   |
10 |     args = FireJobArgs(kw=["--arg1=value1", "--arg2=True", "--arg3=None"])
   |                        ^^
   |
ERROR Unexpected keyword argument `kw` in function `machineconfig.scripts.python.fire_jobs_args_helper.FireJobArgs.__init__` [unexpected-keyword]
  --> .ai/tmp_scripts/test_kw_format.py:18:24
   |
18 |     args = FireJobArgs(kw=["--url=https://example.com/api?param=value"])
   |                        ^^
   |
ERROR Unexpected keyword argument `kw` in function `machineconfig.scripts.python.fire_jobs_args_helper.FireJobArgs.__init__` [unexpected-keyword]
  --> .ai/tmp_scripts/test_kw_format.py:26:24
   |
26 |     args = FireJobArgs(kw=None)
   |                        ^^
   |
ERROR Unexpected keyword argument `kw` in function `machineconfig.scripts.python.fire_jobs_args_helper.FireJobArgs.__init__` [unexpected-keyword]
  --> .ai/tmp_scripts/test_kw_format.py:35:28
   |
35 |         args = FireJobArgs(kw=["invalid_format"])
   |                            ^^
   |
ERROR Unexpected keyword argument `kw` in function `machineconfig.scripts.python.fire_jobs_args_helper.FireJobArgs.__init__` [unexpected-keyword]
  --> .ai/tmp_scripts/test_kw_format.py:43:28
   |
43 |         args = FireJobArgs(kw=["--invalid"])
   |                            ^^
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
ERROR Could not import `main` from `machineconfig.scripts.python.fire_jobs_args_helper` [missing-module-attribute]
  --> .ai/tmp_scripts/test_refactored_fire_args.py:10:64
   |
10 | from machineconfig.scripts.python.fire_jobs_args_helper import main, FireJobArgs
   |                                                                ^^^^
   |
ERROR Could not import `main_from_parser` from `machineconfig.scripts.python.fire_jobs_args_helper` [missing-module-attribute]
  --> .ai/tmp_scripts/test_refactored_fire_args.py:51:72
   |
51 |         from machineconfig.scripts.python.fire_jobs_args_helper import main_from_parser
   |                                                                        ^^^^^^^^^^^^^^^^
   |
ERROR Could not find import of `machineconfig.utils.path_reduced` [import-error]
  --> .ai/tmp_scripts/test_repr_inline.py:10:1
   |
10 | from machineconfig.utils.path_reduced import P
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
ERROR Could not find import of `machineconfig.utils.path_reduced` [import-error]
  --> .ai/tmp_scripts/test_time_deprecation.py:11:1
   |
11 | from machineconfig.utils.path_reduced import P
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/machineconfig/src"]
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
ERROR TypedDict `InstallerData` does not have key `filenameTemplate` [typed-dict-key-error]
  --> src/machineconfig/jobs/python_custom_installers/dev/espanso.py:44:29
   |
44 |                 config_dict["filenameTemplate"]["amd64"]["linux"] = "espanso-debian-wayland-amd64.deb"
   |                             ^^^^^^^^^^^^^^^^^^
   |
ERROR TypedDict `InstallerData` does not have key `filenameTemplate` [typed-dict-key-error]
  --> src/machineconfig/jobs/python_custom_installers/dev/espanso.py:52:29
   |
52 |                 config_dict["filenameTemplate"]["amd64"]["linux"] = "espanso-debian-x11-amd64.deb"
   |                             ^^^^^^^^^^^^^^^^^^
   |
ERROR TypedDict `InstallerData` does not have key `filenameTemplate` [typed-dict-key-error]
  --> src/machineconfig/jobs/python_custom_installers/dev/espanso.py:55:25
   |
55 |             config_dict["filenameTemplate"]["amd64"]["macos"] = "Espanso.dmg"
   |                         ^^^^^^^^^^^^^^^^^^
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
ERROR TODO: Expr::attr_infer_for_type attribute base undefined for type: TypeAlias[Options, type[Literal['⏰ SCHEDULER', '⚙️ DEVAPPS install', '🆕 SYMLINKS new', '🐧 SSH setup wsl', '💾 BACKUP', '📡 SSH setup', '📥 RETRIEVE', '🔄 UPDATE essential repos', '🔐 SSH use key pair to connect two machines', '🔑 SSH add pub key to this machine', '🔗 SYMLINKS, SHELL PROFILE, FONT, TERMINAL SETTINGS.', '🗝️ SSH add identity (private key) to this machine']]] (trying to access __args__) [missing-attribute]
  --> src/machineconfig/scripts/python/devops.py:17:21
   |
17 | options_list = list(Options.__args__)
   |                     ^^^^^^^^^^^^^^^^
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
ERROR Object of class `Installer` has no attribute `get_github_release` [missing-attribute]
  --> src/machineconfig/utils/installer.py:41:49
   |
41 |         _release_url, version_to_be_installed = inst.get_github_release(repo_url=repo_url, version=None)
   |                                                 ^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `object | str` is not assignable to parameter `exe_name` with type `str` in function `machineconfig.utils.installer_utils.installer_class.Installer.check_if_installed_already` [bad-argument-type]
  --> src/machineconfig/utils/installer.py:42:82
   |
42 | ...   verdict, current_ver, new_ver = inst.check_if_installed_already(exe_name=exe_name, version=version_to_be_installed, use_cache=...
   |                                                                                ^^^^^^^^
   |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:136:50
    |
136 |     res_final["OS_SPECIFIC"] = InstallerDataFiles(os_specific_data)
    |                                                  ^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:136:51
    |
136 |     res_final["OS_SPECIFIC"] = InstallerDataFiles(os_specific_data)
    |                                                   ^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:140:49
    |
140 |     res_final["OS_GENERIC"] = InstallerDataFiles(os_generic_data)
    |                                                 ^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:140:50
    |
140 |     res_final["OS_GENERIC"] = InstallerDataFiles(os_generic_data)
    |                                                  ^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:144:54
    |
144 |     res_final["OS_SPECIFIC_DEV"] = InstallerDataFiles(os_specific_dev_data)
    |                                                      ^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:144:55
    |
144 |     res_final["OS_SPECIFIC_DEV"] = InstallerDataFiles(os_specific_dev_data)
    |                                                       ^^^^^^^^^^^^^^^^^^^^
    |
ERROR Missing argument `installers` in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [missing-argument]
   --> src/machineconfig/utils/installer.py:148:53
    |
148 |     res_final["OS_GENERIC_DEV"] = InstallerDataFiles(os_generic_dev_data)
    |                                                     ^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
   --> src/machineconfig/utils/installer.py:148:54
    |
148 |     res_final["OS_GENERIC_DEV"] = InstallerDataFiles(os_generic_dev_data)
    |                                                      ^^^^^^^^^^^^^^^^^^^
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
  --> src/machineconfig/utils/installer_utils/installer_class.py:59:50
   |
59 |         installer_data_files = InstallerDataFiles(config_data)
   |                                                  ^^^^^^^^^^^^^
   |
ERROR Expected argument `version` to be passed by name in function `machineconfig.utils.schemas.installer.installer_types.InstallerDataFiles.__init__` [unexpected-positional-argument]
  --> src/machineconfig/utils/installer_utils/installer_class.py:59:51
   |
59 |         installer_data_files = InstallerDataFiles(config_data)
   |                                                   ^^^^^^^^^^^
   |
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
  --> src/machineconfig/utils/options.py:96:43
   |
96 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR `T` is not assignable to `str` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> src/machineconfig/utils/options.py:99:13
   |
99 |             choice_one: T = default
   |             ^^^^^^^^^^
   |
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
   --> src/machineconfig/utils/options.py:114:47
    |
114 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
    |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
   --> src/machineconfig/utils/options.py:125:47
    |
125 | ...ons(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
    |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> T [closest match]
  (msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = '', tail: str = '', prompt: str = '', default: T | None = None, fzf: bool = False) -> list[T]
ERROR No matching overload found for function `choose_from_options` [no-matching-overload]
   --> src/machineconfig/utils/options.py:162:31
    |
162 |     return choose_from_options(msg="", options=get_ssh_hosts(), multi=multi, fzf=True)
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
