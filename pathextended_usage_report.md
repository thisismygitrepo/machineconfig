# PathExtended Usage Report

This report documents which Python files import `PathExtended` from `machineconfig.utils.path_extended` and which methods they use.

---

## Batch 1: Files 1-10

### 1. `src/machineconfig/utils/installer_utils/installer_runner.py`
- `PathExtended.search()` - Search for files matching pattern
- `PathExtended(path)` - Constructor to create PathExtended instance
- `.delete()` - Delete files/directories
- `.size()` - Get file size

### 2. `src/machineconfig/utils/installer_utils/installer_class.py`
- `PathExtended(url).download()` - Download from URL
- `PathExtended(path)` - Constructor
- `.decompress()` - Decompress archives
- `.with_name()` - Rename file
- `.collapseuser()` - Collapse home directory to placeholder

### 3. `src/machineconfig/jobs/installer/custom/hx.py`
- `PathExtended(path)` - Constructor
- `.search()` - Search for files
- `.delete()` - Delete files/directories
- `.move()` - Move files
- `.copy()` - Copy files

### 4. `src/machineconfig/jobs/installer/custom_dev/bypass_paywall.py`
- `PathExtended(url).download()` - Download from URL
- `.unzip()` - Unzip archive

### 5. `src/machineconfig/utils/installer_utils/installer_locator_utils.py`
- `PathExtended(path)` - Constructor
- `.search()` - Search for files matching pattern
- `.with_name()` - Rename file
- `.size()` - Get file size
- `.chmod()` - Change file permissions
- `.move()` - Move files
- `.delete()` - Delete files/directories

### 6. `src/machineconfig/profile/create_shell_profile.py`
- `PathExtended(path)` - Constructor
- `.collapseuser()` - Collapse home directory to placeholder

### 7. `src/machineconfig/utils/path_helper.py`
- `PathExtended(path)` - Constructor

### 8. `src/machineconfig/utils/terminal.py`
- `PathExtended(path)` - Constructor
- `PathExtended.tmpfile()` - Create temporary file

### 9. `src/machineconfig/jobs/installer/custom_dev/nerfont_windows_helper.py`
- `PathExtended.tmpfile()` - Create temporary file
- `.delete()` - Delete files/directories
- `.search()` - Search for files matching pattern

### 10. `src/machineconfig/profile/create_links.py`
- `PathExtended(path)` - Constructor
- `.search()` - Search for files matching pattern

---

## Batch 2: Files 11-20

### 11. `src/machineconfig/utils/links.py`
- `PathExtended(path)` - Constructor
- `.delete()` - Delete files/directories
- `.symlink_to()` - Create symlink
- `.move()` - Move files
- `.copy()` - Copy files

### 12. `src/machineconfig/scripts/python/croshell.py`
- `PathExtended(path)` - Constructor
- `PathExtended.tmp()` - Get temp directory
- `.with_suffix()` - Change file extension

### 13. `src/machineconfig/scripts/python/helpers_repos/action.py`
- `PathExtended(path)` - Constructor
- `.search()` - Search for files matching pattern

### 14. `src/machineconfig/scripts/python/helpers_repos/grource.py`
- `PathExtended(url).download()` - Download from URL

### 15. `src/machineconfig/scripts/python/helpers_croshell/crosh.py`
- `PathExtended(path)` - Constructor

### 16. `src/machineconfig/scripts/python/helpers_croshell/start_slidev.py`
- `PathExtended(path)` - Constructor
- `.search()` - Search for files matching pattern
- `.copy()` - Copy files
- `.with_name()` - Rename file

### 17. `src/machineconfig/scripts/python/helpers_repos/record.py`
- `PathExtended(path)` - Constructor
- `.collapseuser()` - Collapse home directory to placeholder
- `.search()` - Search for files matching pattern
- `.rel2home()` - Get path relative to home

### 18. `src/machineconfig/scripts/python/helpers_repos/cloud_repo_sync.py`
- `PathExtended(path)` - Constructor
- `.delete()` - Delete files/directories
- `.get_remote_path()` - Get cloud storage path
- `.from_cloud()` - Download from cloud storage
- `.to_cloud()` - Upload to cloud storage
- `.rel2home()` - Get path relative to home

### 19. `src/machineconfig/scripts/python/helpers_repos/sync.py`
- `PathExtended(path)` - Constructor
- `.delete()` - Delete files/directories
- `.to_cloud()` - Upload to cloud storage
- `PathExtended.tmpfile()` - Create temporary file

### 20. `src/machineconfig/scripts/python/helpers_fire_command/fire_jobs_route_helper.py`
- `PathExtended(path)` - Constructor
- `.with_name()` - Rename file
- `PathExtended.tmpfile()` - Create temporary file

---

## Batch 3: Files 21-30

### 21. `src/machineconfig/scripts/python/helpers_repos/action_helper.py`
- `PathExtended` type - Used in dataclass type hints

### 22. `src/machineconfig/scripts/python/helpers_fire_command/file_wrangler.py`
- `PathExtended(path)` - Constructor

### 23. `src/machineconfig/scripts/python/helpers_repos/entrypoint.py`
- `PathExtended(path)` - Constructor
- `.rel2home()` - Get path relative to home

### 24. `src/machineconfig/scripts/python/sessions.py`
- `PathExtended(path)` - Constructor

### 25. `src/machineconfig/setup_windows/wt_and_pwsh/set_wt_settings.py`
- `PathExtended(path)` - Constructor
- `.copy()` - Copy files

### 28. `src/machineconfig/scripts/python/helpers_devops/devops_status.py`
- `PathExtended(path)` - Constructor
- `.collapseuser()` - Collapse home directory to placeholder

### 29. `src/machineconfig/scripts/python/helpers_devops/themes/choose_wezterm_theme.py`
(No relevant methods used)

### 30. `src/machineconfig/scripts/python/helpers_cloud/helpers2.py`
- `PathExtended(path)` - Constructor
- `.get_remote_path()` - Get cloud storage path

---

## Batch 4: Files 31-38

### 31. `src/machineconfig/scripts/python/helpers_cloud/cloud_copy.py`
- `PathExtended(path)` - Constructor
- `.download()` - Download from URL/cloud
- `.decrypt()` - Decrypt file
- `.unzip()` - Unzip archive
- `.search()` - Search for files matching pattern
- `.move()` - Move files
- `.delete()` - Delete files/directories
- `.tmpdir()` - Get temporary directory
- `.from_cloud()` - Download from cloud storage
- `.to_cloud()` - Upload to cloud storage
- `.with_suffix()` - Change file extension
- `.as_url_str()` - Convert path to URL string

### 32. `src/machineconfig/scripts/python/helpers_cloud/cloud_mount.py`
- `PathExtended.tmpfile()` - Create temporary file

### 33. `src/machineconfig/scripts/python/cli_config_dotfile.py`
- `PathExtended(path)` - Constructor

### 34. `src/machineconfig/scripts/python/cli_repos.py`
- `PathExtended(path)` - Constructor
- `.rel2home()` - Get path relative to home
- `.to_cloud()` - Upload to cloud storage

### 35. `src/machineconfig/scripts/python/nw/ftpx.py`
- `PathExtended(path)` - Constructor
- `.collapseuser()` - Collapse home directory to placeholder

### 36. `src/machineconfig/scripts/python/nw/devops_add_identity.py`
- `.search()` - Search for files matching pattern
- `.with_name()` - Rename file
- `.collapseuser()` - Collapse home directory to placeholder

### 37. `src/machineconfig/scripts/python/nw/devops_add_ssh_key.py`
- `PathExtended(path)` - Constructor
- `.search()` - Search for files matching pattern

### 38. `src/machineconfig/scripts/python/nw/mount_ssh.py`
(No relevant methods used)

---

## Batch 5: Files 39-41

### 39. `src/machineconfig/scripts/python/nw/wsl_windows_transfer.py`
- `PathExtended(path)` - Constructor
- `.copy()` - Copy files
- `.rel2home()` - Get path relative to home

---

## Batch 6: Files 42-44

### 42. `src/machineconfig/cluster/remote/distribute.py`
- `PathExtended.home()` - Standard (Path)
- `PathExtended(path)` - Constructor
- `.joinpath()` - Standard (Path)
- `.readit()` - Custom (Unknown Origin)
- `.expanduser()` - Standard (Path)
- `.as_posix()` - Standard (Path)
- `.read_text()` - Standard (Path)
- `.parent` - Standard (Path property)
- `.name` - Standard (Path property)
- `.stem` - Standard (Path property)
- `.relative_to()` - Standard (Path)
- `.collapseuser()` - Custom
- `.listdir()` - Custom (Unknown Origin)

### 43. `src/machineconfig/cluster/remote/job_params.py`
- `PathExtended(path)` - Constructor
- `.expanduser()` - Standard (Path)
- `.absolute()` - Standard (Path)
- `.listdir()` - Custom (Unknown Origin)
- `.collapseuser()` - Custom
- `.as_posix()` - Standard (Path)
- `.name` - Standard (Path property)
- `.stem` - Standard (Path property)
- `.parent` - Standard (Path property)
- `.relative_to()` - Standard (Path)
- `.joinpath()` - Standard (Path)
- `.read_text()` - Standard (Path)

### 44. `src/machineconfig/cluster/remote/run_cluster.py`
- `PathExtended` type - Used in type hints
- `PathExtended(path)` - Constructor (Commented out)

---

## Batch 7: Files 45-47

### 45. `src/machineconfig/cluster/remote/script_execution.py`
- `PathExtended(path)` - Constructor
- `.expanduser()` - Standard (Path)
- `.exists()` - Standard (Path)
- `PathExtended.tmp()` - Custom
- `.mkdir()` - Standard (Path)
- `.collapseuser()` - Custom
- `.as_posix()` - Standard (Path)
- `.joinpath()` - Standard (Path)
- `.write_text()` - Standard (Path)
- `.read_bytes()` - Standard (Path)
- `.copy()` - Custom

### 46. `src/machineconfig/cluster/remote/cloud_manager.py`
- `PathExtended(path)` - Constructor
- `.expanduser()` - Standard (Path)
- `.delete()` - Custom
- `.joinpath()` - Standard (Path)
- `.mkdir()` - Standard (Path)
- `.read_bytes()` - Standard (Path)
- `.read_text()` - Standard (Path)
- `.write_text()` - Standard (Path)
- `.exists()` - Standard (Path)
- `.parent` - Standard (Path property)
- `PathExtended.tmp()` - Custom
- `.from_cloud()` - Custom
- `.get_remote_path()` - Custom
- `.iterdir()` - Standard (Path)
- `.stat()` - Standard (Path)
- `.name` - Standard (Path property)
- `.to_cloud()` - Custom
- `.sync_to_cloud()` - Custom

### 47. `src/machineconfig/cluster/remote/file_manager.py`
- `PathExtended(path)` - Constructor
- `.expanduser()` - Standard (Path)
- `.readit()` - Custom (Unknown Origin)
- `.collapseuser()` - Custom
- `.joinpath()` - Standard (Path)
- `.with_suffix()` - Standard (Path)
- `.write_text()` - Standard (Path)
- `.read_text()` - Standard (Path)
- `.name` - Standard (Path property)
- `.exists()` - Standard (Path)

---

## Batch 8: Files 48-50

### 48. `src/machineconfig/cluster/remote/remote_machine.py`
- `PathExtended` type - Used in type hints
- `PathExtended(path)` - Constructor
- `.parent` - Standard (Path property)
- `.joinpath()` - Standard (Path)
- `.read_text()` - Standard (Path)
- `.expanduser()` - Standard (Path)
- `.name` - Standard (Path property)
- `.write_text()` - Standard (Path)
- `.collapseuser()` - Custom
- `.as_posix()` - Standard (Path)
- `.exists()` - Standard (Path)
- `.rel2home()` - Custom
- `.delete()` - Custom

### 49. `src/machineconfig/cluster/remote/run_remote.py`
- `PathExtended` type - Used in type hints

### 50. `src/machineconfig/cluster/remote/data_transfer.py`
- `PathExtended(path)` - Constructor
- `.expanduser()` - Standard (Path)
- `.zip_n_encrypt()` - Custom
- `.collapseuser()` - Custom
- `.share_on_cloud()` - Custom (Unknown Origin)
- `.download()` - Custom
- `.decrypt_n_unzip()` - Custom
- `.delete()` - Custom
- `.parent` - Standard (Path property)
- `.write_text()` - Standard (Path)
- `.read_text()` - Standard (Path)
- `.rel2home()` - Custom
- `.as_posix()` - Standard (Path)
- `.zip()` - Custom
- `.as_url_str()` - Custom
- `.to_cloud()` - Custom
- `.is_dir()` - Standard (Path)

---

## Batch 9: Files 51-53

### 51. `src/machineconfig/cluster/remote/script_notify_upon_completion.py`
- `PathExtended()` - Constructor
- `.collapseuser()` - Custom
- `.as_posix()` - Standard (Path)
- `.search()` - Custom
- `.print()` - Custom (on result of search)

### 52. `src/machineconfig/utils/scheduling.py`
- `PathExtended` type - Used in type hints
- `PathExtended(path)` - Constructor
- `.expanduser()` - Standard (Path)
- `.absolute()` - Standard (Path)
- `.joinpath()` - Standard (Path)
- `.exists()` - Standard (Path)
- `.parent` - Standard (Path property)
- `.name` - Standard (Path property)
- `PathExtended.tmp()` - Custom
- `.mkdir()` - Standard (Path)
- `.write_text()` - Standard (Path)

### 53. `src/machineconfig/utils/installer_utils/installer_helper.py`
- `PathExtended` type - Used in type hints
- `PathExtended(path)` - Constructor
- `.download()` - Custom
- `.decompress()` - Custom
- `.delete()` - Custom
- `.is_file()` - Standard (Path)
- `.is_dir()` - Standard (Path)
- `.suffixes` - Standard (Path property)
- `.glob()` - Standard (Path)
- `.search()` - Custom

---

## Batch 10: Files 54-56

### 54. `src/machineconfig/utils/installer_utils/install_from_url.py`
- `PathExtended` type - Used in type hints
- `PathExtended(path)` - Constructor
- `.is_file()` - Standard (Path)
- `.suffixes` - Standard (Path property)
- `.decompress()` - Custom
- `.delete()` - Custom
- `.is_dir()` - Standard (Path)
- `.glob()` - Standard (Path)
- `.search()` - Custom

### 55. `src/machineconfig/scripts/python/helpers_croshell/pomodoro.py`
- `PathExtended.tmpfile()` - Custom
- `.parent` - Standard (Path property)
- `.name` - Standard (Path property)

### 56. `src/machineconfig/scripts/python/helpers_croshell/scheduler.py`
- `PathExtended` type - Used in type hints
- `PathExtended(path)` - Constructor
- `.expanduser()` - Standard (Path)
- `.absolute()` - Standard (Path)
- `.joinpath()` - Standard (Path)
- `.exists()` - Standard (Path)
- `.name` - Standard (Path property)
- `.mkdir()` - Standard (Path)
- `.search()` - Custom
- `.filter()` - Custom (on result of search)
- `.write_text()` - Standard (Path)



