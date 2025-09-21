ERROR Could not import `P` from `machineconfig.utils.path_reduced` [missing-module-attribute]
  --> /home/alex/code/machineconfig/.ai/tmp_scripts/test_repr_inline.py:10:46
   |
10 | from machineconfig.utils.path_reduced import P
   |                                              ^
   |
ERROR Could not import `P` from `machineconfig.utils.path_reduced` [missing-module-attribute]
  --> /home/alex/code/machineconfig/.ai/tmp_scripts/test_time_deprecation.py:11:46
   |
11 | from machineconfig.utils.path_reduced import P
   |                                              ^
   |
ERROR Could not import `choose_ssh_host` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/archive/create_zellij_template.py:4:49
  |
4 | from machineconfig.utils.source_of_truth import choose_ssh_host, write_shell_script_to_default_program_path
  |                                                 ^^^^^^^^^^^^^^^
  |
ERROR Could not import `write_shell_script_to_default_program_path` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/archive/create_zellij_template.py:4:66
  |
4 | from machineconfig.utils.source_of_truth import choose_ssh_host, write_shell_script_to_default_program_path
  |                                                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:117:33
    |
117 |                 commands.append(f"# Attach to session '{manager.session_name}':")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:118:33
    |
118 |                 commands.append(f"wt -w {manager.session_name}")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:59:39
   |
59 |                 formatted_args.append(f'"{escaped_arg}"')
   |                                       ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:61:39
   |
61 |                 formatted_args.append(f'"{arg}"')
   |                                       ^^^^^^^^^^
   |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:161:24
    |
161 |                     if proc.info["cmdline"] and len(proc.info["cmdline"]) > 0:
    |                        ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:161:53
    |
161 |                     if proc.info["cmdline"] and len(proc.info["cmdline"]) > 0:
    |                                                     ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:163:28
    |
163 | ...   if proc.info["name"] == cmd or cmd in proc.info["cmdline"][0] or any(cmd in arg for arg in proc.info["cmdline"]):
    |          ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:163:63
    |
163 | ...   if proc.info["name"] == cmd or cmd in proc.info["cmdline"][0] or any(cmd in arg for arg in proc.info["cmdline"]):
    |                                             ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:163:116
    |
163 | ...   if proc.info["name"] == cmd or cmd in proc.info["cmdline"][0] or any(cmd in arg for arg in proc.info["cmdline"]):
    |                                                                                                  ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:164:63
    |
164 | ...   matching_processes.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"], "status": pro...
    |                                         ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:164:89
    |
164 | ...   matching_processes.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"], "status": pro...
    |                                                                   ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:164:119
    |
164 | ...   matching_processes.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"], "status": pro...
    |                                                                                                 ^^^^^^^^^
    |
ERROR Object of class `Process` has no attribute `info` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local.py:164:151
    |
164 | ...c.info["name"], "cmdline": proc.info["cmdline"], "status": proc.info["status"]})
    |                                                               ^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local_manager.py:162:33
    |
162 |                 commands.append(f"# Attach to session '{manager.session_name}':")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
   --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_local_manager.py:163:33
    |
163 |                 commands.append(f"zellij attach {manager.session_name}")
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_utils/layout_generator.py:59:39
   |
59 |                 formatted_args.append(f'"{escaped_arg}"')
   |                                       ^^^^^^^^^^^^^^^^^^
   |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_utils/layout_generator.py:61:39
   |
61 |                 formatted_args.append(f'"{arg}"')
   |                                       ^^^^^^^^^^
   |
ERROR Could not import `symlink_func` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/profile/create.py:8:49
  |
8 | from machineconfig.utils.source_of_truth import symlink_func, symlink_copy, LIBRARY_ROOT, REPO_ROOT, display_options
  |                                                 ^^^^^^^^^^^^
  |
ERROR Could not import `symlink_copy` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/profile/create.py:8:63
  |
8 | from machineconfig.utils.source_of_truth import symlink_func, symlink_copy, LIBRARY_ROOT, REPO_ROOT, display_options
  |                                                               ^^^^^^^^^^^^
  |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/profile/create.py:8:102
  |
8 | from machineconfig.utils.source_of_truth import symlink_func, symlink_copy, LIBRARY_ROOT, REPO_ROOT, display_options
  |                                                                                                      ^^^^^^^^^^^^^^^
  |
ERROR No attribute `windll` in module `ctypes` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/profile/create.py:65:32
   |
65 |                     is_admin = ctypes.windll.shell32.IsUserAnAdmin()
   |                                ^^^^^^^^^^^^^
   |
ERROR Could not import `symlink_copy` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/profile/create_hardlinks.py:9:49
  |
9 | from machineconfig.utils.source_of_truth import symlink_copy as symlink_func, LIBRARY_ROOT, REPO_ROOT, display_options
  |                                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/profile/create_hardlinks.py:9:104
  |
9 | from machineconfig.utils.source_of_truth import symlink_copy as symlink_func, LIBRARY_ROOT, REPO_ROOT, display_options
  |                                                                                                        ^^^^^^^^^^^^^^^
  |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/profile/shell.py:6:74
  |
6 | from machineconfig.utils.source_of_truth import LIBRARY_ROOT, REPO_ROOT, display_options
  |                                                                          ^^^^^^^^^^^^^^^
  |
ERROR Object of class `Path` has no attribute `collapseuser` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/profile/shell.py:30:29
   |
30 |         source = f""". {str(LIBRARY_ROOT.joinpath("settings/shells/pwsh/init.ps1").collapseuser()).replace("~", "$HOME")}"""
   |                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Object of class `Path` has no attribute `collapseuser` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/profile/shell.py:32:34
   |
32 |         source = f"""source {str(LIBRARY_ROOT.joinpath("settings/shells/bash/init.sh").collapseuser()).replace("~", "$HOME")}"""
   |                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Object of class `Path` has no attribute `search` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/profile/shell.py:175:55
    |
175 |     patches: list[str] = [item.as_posix() for item in LIBRARY_ROOT.joinpath(f"profile/patches/{system.lower()}").search()]
    |                                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Could not import `choose_one_option` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/choose_wezterm_theme.py:5:49
  |
5 | from machineconfig.utils.source_of_truth import choose_one_option, PathExtended
  |                                                 ^^^^^^^^^^^^^^^^^
  |
ERROR Could not import `PathExtended` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/choose_wezterm_theme.py:5:68
  |
5 | from machineconfig.utils.source_of_truth import choose_one_option, PathExtended
  |                                                                    ^^^^^^^^^^^^
  |
ERROR Argument `str` is not assignable to parameter `object` with type `LiteralString` in function `list.append` [bad-argument-type]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/choose_wezterm_theme.py:58:30
   |
58 |             res_lines.append(f"config.color_scheme = '{theme}'")
   |                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `choose_one_option` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/cloud_mount.py:3:63
  |
3 | from machineconfig.utils.source_of_truth import PROGRAM_PATH, choose_one_option
  |                                                               ^^^^^^^^^^^^^^^^^
  |
ERROR Could not import `choose_one_option` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/cloud_repo_sync.py:10:91
   |
10 | from machineconfig.utils.source_of_truth import CONFIG_PATH, DEFAULTS_PATH, PROGRAM_PATH, choose_one_option
   |                                                                                           ^^^^^^^^^^^^^^^^^
   |
ERROR Object of class `Path` has no attribute `from_cloud` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/cloud_repo_sync.py:44:9
   |
44 | ...   repo_remote_root.from_cloud(remotepath=remote_path, cloud=cloud_resolved, unzip=True, decrypt=True, rel2home=True, os_specific...
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Object of class `Path` has no attribute `delete` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/cloud_repo_sync.py:80:9
   |
80 |         repo_remote_root.delete(sure=True)
   |         ^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/croshell.py:10:63
   |
10 | from machineconfig.utils.source_of_truth import PROGRAM_PATH, display_options
   |                                                               ^^^^^^^^^^^^^^^
   |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py:3:49
  |
3 | from machineconfig.utils.source_of_truth import display_options, PROGRAM_PATH, write_shell_script_to_default_program_path
  |                                                 ^^^^^^^^^^^^^^^
  |
ERROR Could not import `write_shell_script_to_default_program_path` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py:3:80
  |
3 | from machineconfig.utils.source_of_truth import display_options, PROGRAM_PATH, write_shell_script_to_default_program_path
  |                                                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
ERROR Object of class `Path` has no attribute `delete` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py:74:5
   |
74 |     PROGRAM_PATH.delete(sure=True, verbose=False)
   |     ^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops_add_ssh_key.py:4:63
  |
4 | from machineconfig.utils.source_of_truth import LIBRARY_ROOT, display_options
  |                                                               ^^^^^^^^^^^^^^^
  |
ERROR Could not import `print_code` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops_backup_retrieve.py:6:78
  |
6 | from machineconfig.utils.source_of_truth import LIBRARY_ROOT, DEFAULTS_PATH, print_code, choose_cloud_interactively, choose_multiple_...
  |                                                                              ^^^^^^^^^^
  |
ERROR Could not import `choose_cloud_interactively` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops_backup_retrieve.py:6:90
  |
6 | from machineconfig.utils.source_of_truth import LIBRARY_ROOT, DEFAULTS_PATH, print_code, choose_cloud_interactively, choose_multiple_...
  |                                                                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
ERROR Could not import `choose_multiple_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops_backup_retrieve.py:6:118
  |
6 | ...FAULTS_PATH, print_code, choose_cloud_interactively, choose_multiple_options
  |                                                         ^^^^^^^^^^^^^^^^^^^^^^^
  |
ERROR Could not import `write_shell_script_to_default_program_path` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops_backup_retrieve.py:83:53
   |
83 |     from machineconfig.utils.source_of_truth import write_shell_script_to_default_program_path
   |                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `choose_multiple_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops_devapps_install.py:6:63
  |
6 | from machineconfig.utils.source_of_truth import LIBRARY_ROOT, choose_multiple_options
  |                                                               ^^^^^^^^^^^^^^^^^^^^^^^
  |
ERROR Object of class `Path` has no attribute `collapseuser` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/dotfile.py:47:97
   |
47 | {orig_path.name.split(".")[0]} = {{ this = '{orig_path.collapseuser().as_posix()}', to_this = '{new_path.collapseuser().as_posix()}' }}
   |                                                                                                 ^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_jobs.py:15:49
   |
15 | from machineconfig.utils.source_of_truth import display_options, choose_one_option, PROGRAM_PATH, match_file_name, sanitize_path
   |                                                 ^^^^^^^^^^^^^^^
   |
ERROR Could not import `choose_one_option` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_jobs.py:15:66
   |
15 | from machineconfig.utils.source_of_truth import display_options, choose_one_option, PROGRAM_PATH, match_file_name, sanitize_path
   |                                                                  ^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `match_file_name` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_jobs.py:15:99
   |
15 | from machineconfig.utils.source_of_truth import display_options, choose_one_option, PROGRAM_PATH, match_file_name, sanitize_path
   |                                                                                                   ^^^^^^^^^^^^^^^
   |
ERROR Could not import `sanitize_path` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_jobs.py:15:116
   |
15 | from machineconfig.utils.source_of_truth import display_options, choose_one_option, PROGRAM_PATH, match_file_name, sanitize_path
   |                                                                                                                    ^^^^^^^^^^^^^
   |
ERROR `str` is not assignable to `PathLike[str]` (caused by inconsistent types when breaking cycles) [bad-assignment]
   --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/helpers4.py:148:5
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
   --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/helpers4.py:152:24
    |
152 |                 return path
    |                        ^^^^
    |
ERROR Object of class `Path` has no attribute `from_cloud` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/repo_sync_helpers.py:75:5
   |
75 |     dotfiles_remote.from_cloud(remotepath=remote_path, cloud=cloud_resolved, unzip=True, decrypt=True, rel2home=True, os_specific=Fa...
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
ERROR Object of class `Path` has no attribute `move` [missing-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/repo_sync_helpers.py:80:5
   |
80 |     dotfiles_remote.move(folder=PathExtended.home())
   |     ^^^^^^^^^^^^^^^^^^^^
   |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/mount_nfs.py:6:49
  |
6 | from machineconfig.utils.source_of_truth import display_options, PROGRAM_PATH, choose_ssh_host
  |                                                 ^^^^^^^^^^^^^^^
  |
ERROR Could not import `choose_ssh_host` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/mount_nfs.py:6:80
  |
6 | from machineconfig.utils.source_of_truth import display_options, PROGRAM_PATH, choose_ssh_host
  |                                                                                ^^^^^^^^^^^^^^^
  |
ERROR Could not import `choose_ssh_host` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/mount_ssh.py:7:63
  |
7 | from machineconfig.utils.source_of_truth import PROGRAM_PATH, choose_ssh_host
  |                                                               ^^^^^^^^^^^^^^^
  |
ERROR Object of class `Path` has no attribute `from_cloud` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/repos.py:145:17
    |
145 |                 repos_root.from_cloud(cloud=cloud, rel2home=True)
    |                 ^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Could not import `print_code` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/start_slidev.py:5:76
  |
5 | from machineconfig.utils.source_of_truth import CONFIG_PATH, PROGRAM_PATH, print_code
  |                                                                            ^^^^^^^^^^
  |
ERROR Unexpected keyword argument `inplace` in function `pathlib.PurePath.with_name` [unexpected-keyword]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/start_slidev.py:87:72
   |
87 |         SLIDEV_REPO.joinpath(md_file.name).with_name(name="slides.md", inplace=True, overwrite=True)
   |                                                                        ^^^^^^^
   |
ERROR Unexpected keyword argument `overwrite` in function `pathlib.PurePath.with_name` [unexpected-keyword]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/start_slidev.py:87:86
   |
87 |         SLIDEV_REPO.joinpath(md_file.name).with_name(name="slides.md", inplace=True, overwrite=True)
   |                                                                                      ^^^^^^^^^
   |
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/start_terminals.py:3:63
  |
3 | from machineconfig.utils.source_of_truth import PROGRAM_PATH, display_options
  |                                                               ^^^^^^^^^^^^^^^
  |
ERROR `str | None` is not assignable to `None` (caused by inconsistent types when breaking cycles) [bad-assignment]
  --> /home/alex/code/machineconfig/src/machineconfig/scripts/python/wifi_conn.py:64:13
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
   --> /home/alex/code/machineconfig/src/machineconfig/setup_windows/wt_and_pwsh/set_wt_settings.py:125:22
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
ERROR Argument `str | None` is not assignable to parameter `name` with type `PathLike[bytes] | PathLike[str] | bytes | str` in function `os.makedirs` [bad-argument-type]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/cloud/onedrive/transaction.py:551:21
    |
551 |         os.makedirs(os.path.dirname(file_path), exist_ok=True)
    |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR No matching overload found for function `open` [no-matching-overload]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/cloud/onedrive/transaction.py:553:18
    |
553 |         with open(file_path, "w") as f:
    |                  ^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+a', '+at', '+r', '+rt', '+ta', '+tr', '+tw', '+tx', '+w', '+wt', '+x', '+xt', 'U', 'Ur', 'Urt', 'Utr', 'a', 'a+', 'a+t', 'at', 'at+', 'r', 'r+', 'r+t', 'rU', 'rUt', 'rt', 'rt+', 'rtU', 't+a', 't+r', 't+w', 't+x', 'tUr', 'ta', 'ta+', 'tr', 'tr+', 'trU', 'tw', 'tw+', 'tx', 'tx+', 'w', 'w+', 'w+t', 'wt', 'wt+', 'x', 'x+', 'x+t', 'xt', 'xt+'] = 'r', buffering: int = -1, encoding: str | None = None, errors: str | None = None, newline: str | None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> TextIOWrapper[_WrappedBuffer] [closest match]
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+ab', '+ba', '+br', '+bw', '+bx', '+rb', '+wb', '+xb', 'Ubr', 'Urb', 'a+b', 'ab', 'ab+', 'b+a', 'b+r', 'b+w', 'b+x', 'bUr', 'ba', 'ba+', 'br', 'br+', 'brU', 'bw', 'bw+', 'bx', 'bx+', 'r+b', 'rUb', 'rb', 'rb+', 'rbU', 'w+b', 'wb', 'wb+', 'x+b', 'xb', 'xb+'], buffering: Literal[0], encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> FileIO
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+ab', '+ba', '+br', '+bw', '+bx', '+rb', '+wb', '+xb', 'a+b', 'ab+', 'b+a', 'b+r', 'b+w', 'b+x', 'ba+', 'br+', 'bw+', 'bx+', 'r+b', 'rb+', 'w+b', 'wb+', 'x+b', 'xb+'], buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BufferedRandom
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['ab', 'ba', 'bw', 'bx', 'wb', 'xb'], buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BufferedWriter
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['Ubr', 'Urb', 'bUr', 'br', 'brU', 'rUb', 'rb', 'rbU'], buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BufferedReader[_BufferedReaderStream]
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+ab', '+ba', '+br', '+bw', '+bx', '+rb', '+wb', '+xb', 'Ubr', 'Urb', 'a+b', 'ab', 'ab+', 'b+a', 'b+r', 'b+w', 'b+x', 'bUr', 'ba', 'ba+', 'br', 'br+', 'brU', 'bw', 'bw+', 'bx', 'bx+', 'r+b', 'rUb', 'rb', 'rb+', 'rbU', 'w+b', 'wb', 'wb+', 'x+b', 'xb', 'xb+'], buffering: int = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BinaryIO
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: str, buffering: int = -1, encoding: str | None = None, errors: str | None = None, newline: str | None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> IO[Any]
ERROR Argument `str | None` is not assignable to parameter `path` with type `PathLike[bytes] | PathLike[str] | bytes | int | str` in function `os.chmod` [bad-argument-type]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/cloud/onedrive/transaction.py:557:18
    |
557 |         os.chmod(file_path, 0o600)
    |                  ^^^^^^^^^
    |
ERROR Argument `str | None` is not assignable to parameter `path` with type `PathLike[bytes] | PathLike[str] | bytes | int | str` in function `genericpath.exists` [bad-argument-type]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/cloud/onedrive/transaction.py:581:27
    |
581 |         if os.path.exists(file_path):
    |                           ^^^^^^^^^
    |
ERROR No matching overload found for function `open` [no-matching-overload]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/cloud/onedrive/transaction.py:582:22
    |
582 |             with open(file_path, "r") as f:
    |                      ^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+a', '+at', '+r', '+rt', '+ta', '+tr', '+tw', '+tx', '+w', '+wt', '+x', '+xt', 'U', 'Ur', 'Urt', 'Utr', 'a', 'a+', 'a+t', 'at', 'at+', 'r', 'r+', 'r+t', 'rU', 'rUt', 'rt', 'rt+', 'rtU', 't+a', 't+r', 't+w', 't+x', 'tUr', 'ta', 'ta+', 'tr', 'tr+', 'trU', 'tw', 'tw+', 'tx', 'tx+', 'w', 'w+', 'w+t', 'wt', 'wt+', 'x', 'x+', 'x+t', 'xt', 'xt+'] = 'r', buffering: int = -1, encoding: str | None = None, errors: str | None = None, newline: str | None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> TextIOWrapper[_WrappedBuffer] [closest match]
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+ab', '+ba', '+br', '+bw', '+bx', '+rb', '+wb', '+xb', 'Ubr', 'Urb', 'a+b', 'ab', 'ab+', 'b+a', 'b+r', 'b+w', 'b+x', 'bUr', 'ba', 'ba+', 'br', 'br+', 'brU', 'bw', 'bw+', 'bx', 'bx+', 'r+b', 'rUb', 'rb', 'rb+', 'rbU', 'w+b', 'wb', 'wb+', 'x+b', 'xb', 'xb+'], buffering: Literal[0], encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> FileIO
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+ab', '+ba', '+br', '+bw', '+bx', '+rb', '+wb', '+xb', 'a+b', 'ab+', 'b+a', 'b+r', 'b+w', 'b+x', 'ba+', 'br+', 'bw+', 'bx+', 'r+b', 'rb+', 'w+b', 'wb+', 'x+b', 'xb+'], buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BufferedRandom
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['ab', 'ba', 'bw', 'bx', 'wb', 'xb'], buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BufferedWriter
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['Ubr', 'Urb', 'bUr', 'br', 'brU', 'rUb', 'rb', 'rbU'], buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BufferedReader[_BufferedReaderStream]
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: Literal['+ab', '+ba', '+br', '+bw', '+bx', '+rb', '+wb', '+xb', 'Ubr', 'Urb', 'a+b', 'ab', 'ab+', 'b+a', 'b+r', 'b+w', 'b+x', 'bUr', 'ba', 'ba+', 'br', 'br+', 'brU', 'bw', 'bw+', 'bx', 'bx+', 'r+b', 'rUb', 'rb', 'rb+', 'rbU', 'w+b', 'wb', 'wb+', 'x+b', 'xb', 'xb+'], buffering: int = -1, encoding: None = None, errors: None = None, newline: None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> BinaryIO
  (file: PathLike[bytes] | PathLike[str] | bytes | int | str, mode: str, buffering: int = -1, encoding: str | None = None, errors: str | None = None, newline: str | None = None, closefd: bool = True, opener: ((str, int) -> int) | None = None) -> IO[Any]
ERROR Could not find name `PROGRAM_PATH` [unknown-name]
  --> /home/alex/code/machineconfig/src/machineconfig/utils/code.py:85:73
   |
85 |         print_code(code=program, lexer="shell", desc=desc, subtitle=str(PROGRAM_PATH))
   |                                                                         ^^^^^^^^^^^^
   |
ERROR Could not find name `PROGRAM_PATH` [unknown-name]
  --> /home/alex/code/machineconfig/src/machineconfig/utils/code.py:86:5
   |
86 |     PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
   |     ^^^^^^^^^^^^
   |
ERROR Could not find name `PROGRAM_PATH` [unknown-name]
  --> /home/alex/code/machineconfig/src/machineconfig/utils/code.py:87:5
   |
87 |     PROGRAM_PATH.write_text(program, encoding="utf-8")
   |     ^^^^^^^^^^^^
   |
ERROR Could not find name `PROGRAM_PATH` [unknown-name]
  --> /home/alex/code/machineconfig/src/machineconfig/utils/code.py:89:38
   |
89 |         result = subprocess.run(f". {PROGRAM_PATH}", shell=True, capture_output=True, text=True)
   |                                      ^^^^^^^^^^^^
   |
ERROR Object of class `Path` has no attribute `delete` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/installer.py:174:9
    |
174 |         INSTALL_VERSION_ROOT.delete(sure=True)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Could not import `check_tool_exists` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/utils/installer_utils/installer_class.py:3:102
  |
3 | from machineconfig.utils.source_of_truth import INSTALL_TMP_DIR, INSTALL_VERSION_ROOT, LIBRARY_ROOT, check_tool_exists
  |                                                                                                      ^^^^^^^^^^^^^^^^^
  |
ERROR Could not import `choose_one_option` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
  --> /home/alex/code/machineconfig/src/machineconfig/utils/installer_utils/installer_class.py:64:57
   |
64 |         from machineconfig.utils.source_of_truth import choose_one_option
   |                                                         ^^^^^^^^^^^^^^^^^
   |
ERROR `T` is not assignable to `str` (caused by inconsistent types when breaking cycles) [bad-assignment]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/options.py:103:13
    |
103 |             choice_one: T = default
    |             ^^^^^^^^^^
    |
ERROR No matching overload found for function `tarfile.TarFile.open` [no-matching-overload]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/path_reduced.py:219:26
    |
219 |         with tarfile.open(str(path), mode) as file:
    |                          ^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (name: PathLike[bytes] | PathLike[str] | bytes | str | None = None, mode: Literal['r', 'r:', 'r:*', 'r:bz2', 'r:gz', 'r:xz'] = 'r', fileobj: _Fileobj | None = None, bufsize: int = 10240, *, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ...) -> TarFile [closest match]
  (name: PathLike[bytes] | PathLike[str] | bytes | str | None, mode: Literal['a', 'a:', 'w', 'w:', 'w:tar', 'x', 'x:'], fileobj: _Fileobj | None = None, bufsize: int = 10240, *, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ...) -> TarFile
  (name: PathLike[bytes] | PathLike[str] | bytes | str | None = None, *, mode: Literal['a', 'a:', 'w', 'w:', 'w:tar', 'x', 'x:'], fileobj: _Fileobj | None = None, bufsize: int = 10240, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ...) -> TarFile
  (name: PathLike[bytes] | PathLike[str] | bytes | str | None, mode: Literal['w:bz2', 'w:gz', 'x:bz2', 'x:gz'], fileobj: _Fileobj | None = None, bufsize: int = 10240, *, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ..., compresslevel: int = 9) -> TarFile
  (name: PathLike[bytes] | PathLike[str] | bytes | str | None = None, *, mode: Literal['w:bz2', 'w:gz', 'x:bz2', 'x:gz'], fileobj: _Fileobj | None = None, bufsize: int = 10240, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ..., compresslevel: int = 9) -> TarFile
  (name: PathLike[bytes] | PathLike[str] | bytes | str | None, mode: Literal['w:xz', 'x:xz'], fileobj: _Fileobj | None = None, bufsize: int = 10240, *, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ..., preset: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None = ...) -> TarFile
  (name: PathLike[bytes] | PathLike[str] | bytes | str | None = None, *, mode: Literal['w:xz', 'x:xz'], fileobj: _Fileobj | None = None, bufsize: int = 10240, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ..., preset: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None = ...) -> TarFile
  (name: Buffer | PathLike[bytes] | PathLike[str] | bytes | str | None, mode: Literal['r|', 'r|*', 'r|bz2', 'r|gz', 'r|xz', 'r|zst'], fileobj: _Fileobj | None = None, bufsize: int = 10240, *, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ...) -> TarFile
  (name: Buffer | PathLike[bytes] | PathLike[str] | bytes | str | None = None, *, mode: Literal['r|', 'r|*', 'r|bz2', 'r|gz', 'r|xz', 'r|zst'], fileobj: _Fileobj | None = None, bufsize: int = 10240, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ...) -> TarFile
  (name: Buffer | PathLike[bytes] | PathLike[str] | bytes | str | None, mode: Literal['w|', 'w|xz', 'w|zst'], fileobj: _Fileobj | None = None, bufsize: int = 10240, *, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ...) -> TarFile
  (name: Buffer | PathLike[bytes] | PathLike[str] | bytes | str | None = None, *, mode: Literal['w|', 'w|xz', 'w|zst'], fileobj: _Fileobj | None = None, bufsize: int = 10240, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ...) -> TarFile
  (name: Buffer | PathLike[bytes] | PathLike[str] | bytes | str | None, mode: Literal['w|bz2', 'w|gz'], fileobj: _Fileobj | None = None, bufsize: int = 10240, *, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ..., compresslevel: int = 9) -> TarFile
  (name: Buffer | PathLike[bytes] | PathLike[str] | bytes | str | None = None, *, mode: Literal['w|bz2', 'w|gz'], fileobj: _Fileobj | None = None, bufsize: int = 10240, format: int | None = ..., tarinfo: type[TarInfo] | None = ..., dereference: bool | None = ..., ignore_zeros: bool | None = ..., encoding: str | None = ..., errors: str = ..., pax_headers: Mapping[str, str] | None = ..., debug: int | None = ..., errorlevel: int | None = ..., compresslevel: int = 9) -> TarFile
ERROR Object of class `str` has no attribute `suffixes` [missing-attribute]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/path_reduced.py:378:41
    |
378 |         full_suffix = suffix or "".join(("bruh" + self).suffixes)
    |                                         ^^^^^^^^^^^^^^^^^^^^^^^^
    |
ERROR Could not find import of `win32com.shell.shell` [import-error]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/path_reduced.py:533:20
    |
533 |             import win32com.shell.shell
    |                    ^^^^^^^^^^^^^^^^^^^^
    |
  Looked in these locations (from default config for project root marked by `/home/alex/code/machineconfig/pyproject.toml`):
  Import root (inferred from project layout): "/home/alex/code/machineconfig/src"
  Site package path queried from interpreter: ["/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13", "/home/alex/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/lib-dynload", "/home/alex/code/machineconfig/.venv/lib/python3.13/site-packages", "/home/alex/code/crocodile/myresources", "/home/alex/code/machineconfig/src"]
ERROR Could not import `display_options` from `machineconfig.utils.source_of_truth` [missing-module-attribute]
 --> /home/alex/code/machineconfig/src/machineconfig/utils/procs.py:6:49
  |
6 | from machineconfig.utils.source_of_truth import display_options
  |                                                 ^^^^^^^^^^^^^^^
  |
ERROR No matching overload found for function `type.__new__` [no-matching-overload]
   --> /home/alex/code/machineconfig/src/machineconfig/utils/ssh.py:126:30
    |
126 |         self.tqdm_wrap = type("TqdmWrap", (tqdm,), {"view_bar": view_bar})
    |                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
  Possible overloads:
  (cls: type[type], o: object, /) -> type [closest match]
  (cls: type[TypeVar[Self]], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwds: Any) -> TypeVar[Self]
ERROR No matching overload found for function `type.__new__` [no-matching-overload]
  --> /home/alex/code/machineconfig/src/machineconfig/utils/utils2.py:53:17
   |
53 |     inspect(type("TempStruct", (object,), obj)(), value=False, title=title, docs=False, dunder=False, sort=False)
   |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
  Possible overloads:
  (cls: type[type], o: object, /) -> type [closest match]
  (cls: type[TypeVar[Self]], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwds: Any) -> TypeVar[Self]
