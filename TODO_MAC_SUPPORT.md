# Mac (Darwin) Support TODO

This file tracks the progress of adding Mac support to Python files that check for system types.

## Files to check for Mac support:

- [ ] test_session_manager.py
- [ ] src/__init__.py
- [ ] src/machineconfig/__init__.py
- [ ] src/machineconfig/profile/__init__.py
- [ ] src/machineconfig/utils/utils2.py
- [ ] src/machineconfig/utils/procs.py
- [ ] src/machineconfig/utils/ve.py
- [ ] src/machineconfig/profile/shell.py
- [ ] src/machineconfig/utils/path.py
- [ ] src/machineconfig/utils/scheduling.py
- [ ] src/machineconfig/jobs/python_linux_installers/__init__.py
- [ ] src/machineconfig/jobs/__init__.py
- [ ] src/machineconfig/jobs/python/tasks.py
- [ ] src/machineconfig/jobs/python/__init__.py
- [ ] src/machineconfig/jobs/python/create_bootable_media.py
- [ ] src/machineconfig/jobs/python/checkout_version.py
- [ ] src/machineconfig/jobs/python/python_ve_symlink.py
- [ ] src/machineconfig/jobs/python_linux_installers/dev/__init__.py
- [ ] src/machineconfig/jobs/python/python_cargo_build_share.py
- [ ] src/machineconfig/jobs/python/check_installations.py
- [ ] src/machineconfig/jobs/python/python_custom_create_shortcuts.py
- [ ] src/machineconfig/jobs/python/python_get_site_packages.py
- [ ] src/machineconfig/jobs/python/python_global_installs.py
- [ ] src/machineconfig/jobs/python/python_run_shell_scripts.py
- [ ] src/machineconfig/jobs/python_linux_installers/dev/lvim.py
- [ ] src/machineconfig/jobs/python/python_repo_management.py
- [ ] src/machineconfig/jobs/python_linux_installers/dev/neovim.py
- [ ] src/machineconfig/jobs/python_linux_installers/dev/others.py
- [ ] src/machineconfig/jobs/python_linux_installers/dev/rust.py
- [ ] src/machineconfig/jobs/python/vscode/api.py
- [ ] src/machineconfig/jobs/python/vscode/__init__.py
- [ ] src/machineconfig/jobs/python/vscode/extensions.py
- [ ] src/machineconfig/jobs/python/vscode/link_ve.py
- [ ] src/machineconfig/jobs/python/vscode/select_interpreter.py
- [ ] src/machineconfig/jobs/python_custom_installers/__init__.py
- [ ] src/machineconfig/jobs/python_custom_installers/github.py
- [ ] src/machineconfig/jobs/python_custom_installers/kaggle.py
- [ ] src/machineconfig/jobs/python_custom_installers/others.py
- [ ] src/machineconfig/jobs/python_custom_installers/rust.py
- [ ] src/machineconfig/jobs/python_custom_installers/rustdesk.py
- [ ] src/machineconfig/jobs/python_generic_installers/__init__.py
- [ ] src/machineconfig/jobs/python_generic_installers/packages_generic.py
- [ ] src/machineconfig/jobs/python_generic_installers/packages_poetry.py
- [ ] src/machineconfig/jobs/python_generic_installers/packages_uv.py
- [ ] src/machineconfig/jobs/python_generic_installers/python_download.py
- [ ] src/machineconfig/jobs/python_linux_installers/__init__.py
- [ ] src/machineconfig/jobs/python_linux_installers/apt.py
- [ ] src/machineconfig/jobs/python_linux_installers/system.py
- [ ] src/machineconfig/jobs/python_windows_installers/__init__.py
- [ ] src/machineconfig/jobs/python_windows_installers/choco.py
- [ ] src/machineconfig/jobs/python_windows_installers/scoop.py
- [ ] src/machineconfig/jobs/python_windows_installers/winget.py
- [ ] src/machineconfig/jobs/linux/__init__.py
- [ ] src/machineconfig/jobs/linux/bash.py
- [ ] src/machineconfig/jobs/linux/symlinks.py
- [ ] src/machineconfig/jobs/windows/__init__.py
- [ ] src/machineconfig/jobs/windows/powershell.py
- [ ] src/machineconfig/jobs/windows/shortcuts.py
- [ ] src/machineconfig/jobs/windows/symlinks.py
- [ ] src/machineconfig/cluster/__init__.py
- [ ] src/machineconfig/cluster/cloud_manager.py
- [ ] src/machineconfig/cluster/data_transfer.py
- [ ] src/machineconfig/cluster/distribute.py
- [ ] src/machineconfig/cluster/file_manager.py
- [ ] src/machineconfig/cluster/job_params.py
- [ ] src/machineconfig/cluster/loader_runner.py
- [ ] src/machineconfig/cluster/remote_machine.py
- [ ] src/machineconfig/cluster/script_execution.py
- [ ] src/machineconfig/cluster/script_notify_upon_completion.py
- [ ] src/machineconfig/cluster/self_ssh.py
- [ ] src/machineconfig/cluster/sessions_managers/__init__.py
- [ ] src/machineconfig/cluster/sessions_managers/mprocs.py
- [ ] src/machineconfig/cluster/sessions_managers/screen.py
- [ ] src/machineconfig/cluster/sessions_managers/tmux.py
- [ ] src/machineconfig/cluster/sessions_managers/zellij.py
- [ ] src/machineconfig/utils/__init__.py
- [ ] src/machineconfig/utils/invoker.py
- [ ] src/machineconfig/utils/logger.py
- [ ] src/machineconfig/utils/misc.py
- [ ] src/machineconfig/utils/networking.py
- [ ] src/machineconfig/utils/os.py
- [ ] src/machineconfig/utils/platform_info.py
- [ ] src/machineconfig/utils/read_csv.py
- [ ] src/machineconfig/utils/shell.py
- [ ] src/machineconfig/utils/test_str_utils.py
- [ ] src/machineconfig/utils/str_utils.py
- [ ] src/machineconfig/profile/create_hardlinks.py
- [ ] src/machineconfig/profile/create.py
- [ ] src/machineconfig/scripts/__init__.py
- [ ] src/machineconfig/scripts/cloud/__init__.py
- [ ] src/machineconfig/scripts/cloud/azure.py
- [ ] src/machineconfig/scripts/cloud/databricks.py
- [ ] src/machineconfig/scripts/python/__init__.py
- [ ] src/machineconfig/scripts/python/fire.py
- [ ] src/machineconfig/scripts/python/test_notebook.py
- [ ] src/machineconfig/scripts/windows/__init__.py
- [ ] src/machineconfig/scripts/windows/symlinks.py
- [ ] src/machineconfig/scripts/linux/__init__.py
- [ ] src/machineconfig/scripts/linux/symlinks.py
- [ ] src/machineconfig/settings/__init__.py

---

## Progress Log:
*Files checked and updated will be documented here*

### ✅ COMPLETED:
1. **src/machineconfig/utils/options.py** - Added Darwin support to `check_tool_exists()` function. Now supports `which` command on both Linux and macOS.
2. **src/machineconfig/utils/code.py** - Added Darwin support to shell script functions. Mac now uses bash scripts like Linux.
3. **src/machineconfig/utils/scheduling.py** - Added Darwin support to task execution. Mac uses bash like Linux.
4. **src/machineconfig/utils/ve.py** - Updated type hints and logic to support Darwin virtual environments.
5. **src/machineconfig/utils/installer.py** - Added Mac support with Homebrew paths (/opt/homebrew/bin).
6. **src/machineconfig/utils/installer_utils/installer_class.py** - Added Darwin support throughout installer class.
7. **src/machineconfig/jobs/python/python_cargo_build_share.py** - Added Mac support for Rust tool installation.
8. **src/machineconfig/jobs/python_custom_installers/hx.py** - Added macOS support for Helix editor installation.
9. **src/machineconfig/jobs/python_custom_installers/gh.py** - Added macOS support for GitHub CLI installation.
10. **src/machineconfig/cluster/script_execution.py** - Added Darwin support for session management and script execution.
11. **src/machineconfig/utils/path.py** - Added comprehensive Mac path support (handling /Users/ paths).
12. **src/machineconfig/jobs/python/check_installations.py** - Added Darwin support for app installation to /usr/local/bin.
13. **src/machineconfig/scripts/python/fire_jobs.py** - Added Darwin support for Python path export and loop commands.
14. **src/machineconfig/jobs/python_custom_installers/docker.py** - Added macOS support using Homebrew.
15. **src/machineconfig/jobs/python_custom_installers/dev/alacritty.py** - Added macOS support for Alacritty terminal.
16. **src/machineconfig/jobs/python_custom_installers/dev/espanso.py** - Added macOS support for Espanso text expander.
17. **src/machineconfig/jobs/python_custom_installers/dev/redis.py** - Added macOS support using Homebrew.
18. **src/machineconfig/jobs/python_custom_installers/dev/lvim.py** - Added macOS support for LunarVim.
19. **src/machineconfig/jobs/python_custom_installers/dev/brave.py** - Added macOS support using Homebrew cask.
20. **src/machineconfig/jobs/python_custom_installers/dev/wezterm.py** - Added macOS support using Homebrew cask.
21. **src/machineconfig/jobs/python_custom_installers/dev/nerdfont.py** - Added basic macOS support.
22. **src/machineconfig/jobs/python_custom_installers/warp-cli.py** - Added basic macOS support.
23. **src/machineconfig/jobs/python_custom_installers/archive/ngrok.py** - Added basic macOS support.
24. **src/machineconfig/cluster/self_ssh.py** - Added Darwin support for SSH session management.
25. **src/machineconfig/scripts/python/cloud_mount.py** - Added Darwin support for cloud mounting.
26. **src/machineconfig/scripts/python/wifi_conn.py** - Added partial Darwin support (needs more work for full macOS WiFi support).
27. **src/machineconfig/scripts/python/helpers/repo_sync_helpers.py** - Added Darwin support for repository inspection.
28. **src/machineconfig/scripts/python/mount_nfs.py** - Added Darwin support for NFS mounting.
29. **src/machineconfig/scripts/python/mount_nw_drive.py** - Added Darwin support for network drive mounting.
30. **src/machineconfig/scripts/python/cloud_repo_sync.py** - Added Darwin support for repository syncing.
31. **src/machineconfig/jobs/python_custom_installers/dev/code.py** - Added macOS support for VS Code installation using Homebrew.

### 📝 NOTES:
- **Virtual Environment Support**: The `ve_utils/ve1.py` file already had excellent Darwin support implemented.
- **VS Code Select Interpreter**: The `vscode/select_interpreter.py` file already had complete Darwin support.
- **Path Handling**: Enhanced macOS support to handle both `/Users/` (macOS) and `/home/` (Linux) path structures.
- **Homebrew Integration**: Many macOS installations now use Homebrew for package management.
- **WiFi Support**: Basic macOS WiFi support added, but full implementation would require significant work with `networksetup` commands.

### 🔍 REMAINING WORK:
- **WiFi Management**: Complete macOS WiFi functionality implementation
- **Platform-Specific Optimizations**: Some installers may need macOS-specific configuration paths
- **Testing**: All changes should be tested on actual macOS systems
