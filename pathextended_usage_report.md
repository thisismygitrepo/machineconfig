# PathExtended Usage Report

This report documents which Python files import `PathExtended` from `machineconfig.utils.path_extended` and which methods they use.
Files are ordered from least to most use of custom methods (not inherited methods of pathlib).


---

## 1 Custom Method

### 1. `src/machineconfig/scripts/python/helpers_cloud/cloud_mount.py`
- `.print()` - Print path
- `PathExtended(path)` - Constructor

### 2. `src/machineconfig/scripts/python/helpers_croshell/pomodoro.py`
- `.tmpfile()` - Create temporary file

### 3. `src/machineconfig/scripts/python/helpers_croshell/scheduler.py`
- `.append()` - Append suffix/name

### 4. `src/machineconfig/scripts/python/helpers_devops/cli_repos.py`
- `.to_cloud()` - Upload to cloud storage
- `PathExtended(path)` - Constructor

### 5. `src/machineconfig/scripts/python/helpers_repos/entrypoint.py`
- `.from_cloud()` - Download from cloud storage
- `PathExtended(path)` - Constructor

### 6. `src/machineconfig/utils/terminal.py`
- `.print()` - Print path
- `PathExtended(path)` - Constructor

## 2 Custom Methods

### 7. `src/machineconfig/profile/create_shell_profile.py`
- `.collapseuser()` - Collapse home directory to placeholder
- `.print()` - Print path
- `PathExtended(path)` - Constructor

### 8. `src/machineconfig/scripts/python/croshell.py`
- `.print()` - Print path
- `.with_suffix()` - Change file extension

### 9. `src/machineconfig/scripts/python/helpers_croshell/viewer.py`
- `.split()` - Split path
- `.tmpdir()` - Get temporary directory

### 10. `src/machineconfig/scripts/python/helpers_repos/action.py`
- `.append()` - Append suffix/name
- `.search()` - Search for files matching pattern

## 3 Custom Methods

### 11. `src/machineconfig/cluster/remote/script_notify_upon_completion.py`
- `.collapseuser()` - Collapse home directory to placeholder
- `.print()` - Print path
- `.search()` - Search for files matching pattern

### 12. `src/machineconfig/jobs/installer/python_scripts/bypass_paywall.py`
- `.download()` - Download from URL
- `.print()` - Print path
- `.unzip()` - Unzip archive
- `PathExtended(path)` - Constructor

### 13. `src/machineconfig/jobs/installer/python_scripts/nerfont_windows_helper.py`
- `.append()` - Append suffix/name
- `.delete()` - Delete files/directories
- `.print()` - Print path
- `PathExtended(path)` - Constructor

### 14. `src/machineconfig/profile/create_links.py`
- `.append()` - Append suffix/name
- `.print()` - Print path
- `.split()` - Split path
- `PathExtended(path)` - Constructor

### 15. `src/machineconfig/scripts/python/ftpx.py`
- `.collapseuser()` - Collapse home directory to placeholder
- `.print()` - Print path
- `.split()` - Split path
- `PathExtended(path)` - Constructor

### 16. `src/machineconfig/scripts/python/helpers_cloud/helpers2.py`
- `.get_remote_path()` - Get cloud storage path
- `.print()` - Print path
- `.split()` - Split path
- `PathExtended(path)` - Constructor

### 17. `src/machineconfig/scripts/python/helpers_repos/record.py`
- `.append()` - Append suffix/name
- `.collapseuser()` - Collapse home directory to placeholder
- `.search()` - Search for files matching pattern
- `PathExtended(path)` - Constructor

### 18. `src/machineconfig/scripts/python/helpers_repos/sync.py`
- `.delete()` - Delete files/directories
- `.print()` - Print path
- `.to_cloud()` - Upload to cloud storage
- `PathExtended(path)` - Constructor

### 19. `src/machineconfig/settings/shells/ipy/profiles/default/startup/playext.py`
- `.append()` - Append suffix/name
- `.print()` - Print path
- `.tmp()` - Get temp directory/file

### 20. `src/machineconfig/utils/installer_utils/install_from_url.py`
- `.append()` - Append suffix/name
- `.print()` - Print path
- `.split()` - Split path

### 21. `src/machineconfig/utils/installer_utils/installer_class.py`
- `.append()` - Append suffix/name
- `.split()` - Split path
- `.with_name()` - Rename file

## 4 Custom Methods

### 22. `.ai/tmp_scripts/generate_pathextended_report.py`
- `.append()` - Append suffix/name
- `.search()` - Search for files matching pattern
- `.split()` - Split path
- `.tmpfile()` - Create temporary file

### 23. `src/machineconfig/cluster/remote/distribute.py`
- `.append()` - Append suffix/name
- `.print()` - Print path
- `.readit()` - Read file content (Custom)
- `.split()` - Split path

### 24. `src/machineconfig/cluster/remote/script_execution.py`
- `.collapseuser()` - Collapse home directory to placeholder
- `.copy()` - Copy files
- `.print()` - Print path
- `.tmp()` - Get temp directory/file

### 25. `src/machineconfig/jobs/installer/python_scripts/hx.py`
- `.copy()` - Copy files
- `.delete()` - Delete files/directories
- `.move()` - Move files
- `.print()` - Print path
- `PathExtended(path)` - Constructor

### 26. `src/machineconfig/scripts/python/helpers_croshell/start_slidev.py`
- `.copy()` - Copy files
- `.print()` - Print path
- `.split()` - Split path
- `.with_name()` - Rename file
- `PathExtended(path)` - Constructor

### 27. `src/machineconfig/scripts/python/helpers_network/ssh_add_identity.py`
- `.collapseuser()` - Collapse home directory to placeholder
- `.print()` - Print path
- `.split()` - Split path
- `.with_name()` - Rename file
- `PathExtended(path)` - Constructor

### 28. `src/machineconfig/scripts/python/helpers_repos/grource.py`
- `.append()` - Append suffix/name
- `.download()` - Download from URL
- `.resolve()` - Resolve path
- `.split()` - Split path
- `PathExtended(path)` - Constructor

### 29. `src/machineconfig/settings/wt/set_wt_settings.py`
- `.append()` - Append suffix/name
- `.copy()` - Copy files
- `.print()` - Print path
- `.split()` - Split path
- `PathExtended(path)` - Constructor

### 30. `src/machineconfig/utils/installer_utils/installer_runner.py`
- `.append()` - Append suffix/name
- `.delete()` - Delete files/directories
- `.print()` - Print path
- `.resolve()` - Resolve path
- `PathExtended(path)` - Constructor

### 31. `src/machineconfig/utils/scheduling.py`
- `.append()` - Append suffix/name
- `.print()` - Print path
- `.split()` - Split path
- `.tmp()` - Get temp directory/file

## 5 Custom Methods

### 32. `src/machineconfig/cluster/remote/file_manager.py`
- `.append()` - Append suffix/name
- `.collapseuser()` - Collapse home directory to placeholder
- `.print()` - Print path
- `.readit()` - Read file content (Custom)
- `.with_suffix()` - Change file extension

### 33. `src/machineconfig/cluster/remote/job_params.py`
- `.append()` - Append suffix/name
- `.collapseuser()` - Collapse home directory to placeholder
- `.listdir()` - List directory (Custom)
- `.readit()` - Read file content (Custom)
- `.split()` - Split path

### 34. `src/machineconfig/scripts/python/helpers_devops/devops_status.py`
- `.append()` - Append suffix/name
- `.collapseuser()` - Collapse home directory to placeholder
- `.print()` - Print path
- `.split()` - Split path
- `.with_suffix()` - Change file extension
- `PathExtended(path)` - Constructor

### 35. `src/machineconfig/scripts/python/helpers_repos/cloud_repo_sync.py`
- `.delete()` - Delete files/directories
- `.from_cloud()` - Download from cloud storage
- `.get_remote_path()` - Get cloud storage path
- `.print()` - Print path
- `.to_cloud()` - Upload to cloud storage
- `PathExtended(path)` - Constructor

### 36. `src/machineconfig/utils/installer_utils/installer_helper.py`
- `.append()` - Append suffix/name
- `.decompress()` - Decompress archives
- `.delete()` - Delete files/directories
- `.download()` - Download from URL
- `.print()` - Print path
- `PathExtended(path)` - Constructor

### 37. `src/machineconfig/utils/installer_utils/installer_locator_utils.py`
- `.chmod()` - Change file permissions
- `.delete()` - Delete files/directories
- `.move()` - Move files
- `.split()` - Split path
- `.with_name()` - Rename file
- `PathExtended(path)` - Constructor

## 7 Custom Methods

### 38. `src/machineconfig/utils/links.py`
- `.append()` - Append suffix/name
- `.copy()` - Copy files
- `.delete()` - Delete files/directories
- `.move()` - Move files
- `.print()` - Print path
- `.resolve()` - Resolve path
- `.symlink_to()` - Create symlink
- `PathExtended(path)` - Constructor

## 8 Custom Methods

### 39. `src/machineconfig/cluster/remote/remote_machine.py`
- `.append()` - Append suffix/name
- `.collapseuser()` - Collapse home directory to placeholder
- `.delete()` - Delete files/directories
- `.print()` - Print path
- `.readit()` - Read file content (Custom)
- `.rel2home()` - Get path relative to home
- `.split()` - Split path
- `.to_cloud()` - Upload to cloud storage

### 40. `src/machineconfig/jobs/installer/check_installations.py`
- `.append()` - Append suffix/name
- `.collapseuser()` - Collapse home directory to placeholder
- `.download()` - Download from URL
- `.move()` - Move files
- `.search()` - Search for files matching pattern
- `.split()` - Split path
- `.to_cloud()` - Upload to cloud storage
- `.with_suffix()` - Change file extension

## 9 Custom Methods

### 41. `src/machineconfig/cluster/remote/cloud_manager.py`
- `.append()` - Append suffix/name
- `.copy()` - Copy files
- `.delete()` - Delete files/directories
- `.from_cloud()` - Download from cloud storage
- `.get_remote_path()` - Get cloud storage path
- `.print()` - Print path
- `.sync_to_cloud()` - Sync to cloud storage
- `.tmp()` - Get temp directory/file
- `.to_cloud()` - Upload to cloud storage

## 10 Custom Methods

### 42. `src/machineconfig/cluster/remote/data_transfer.py`
- `.as_url_str()` - Convert path to URL string
- `.collapseuser()` - Collapse home directory to placeholder
- `.decrypt_n_unzip()` - Decrypt and unzip
- `.delete()` - Delete files/directories
- `.download()` - Download from URL
- `.rel2home()` - Get path relative to home
- `.share_on_cloud()` - Share on cloud
- `.to_cloud()` - Upload to cloud storage
- `.zip()` - Zip files
- `.zip_n_encrypt()` - Zip and encrypt

## 12 Custom Methods

### 43. `src/machineconfig/scripts/python/helpers_cloud/cloud_copy.py`
- `.as_url_str()` - Convert path to URL string
- `.decrypt()` - Decrypt file
- `.delete()` - Delete files/directories
- `.download()` - Download from URL
- `.from_cloud()` - Download from cloud storage
- `.move()` - Move files
- `.print()` - Print path
- `.split()` - Split path
- `.to_cloud()` - Upload to cloud storage
- `.unzip()` - Unzip archive
- `.with_suffix()` - Change file extension
- `PathExtended(path)` - Constructor
- `PathExtended.tmpdir()` - Get temporary directory

## 25 Custom Methods

### 44. `src/machineconfig/utils/path_extended.py`
- `.append()` - Append suffix/name
- `.as_url_str()` - Convert path to URL string
- `.as_zip_path()` - Get zip path
- `.clickable()` - Get clickable URI
- `.copy()` - Copy files
- `.decompress()` - Decompress archives
- `.decrypt()` - Decrypt file
- `.delete()` - Delete files/directories
- `.encrypt()` - Encrypt file
- `.filter()` - Filter results
- `.get_remote_path()` - Get cloud storage path
- `.move()` - Move files
- `.print()` - Print path
- `.resolve()` - Resolve path
- `.search()` - Search for files matching pattern
- `.split()` - Split path
- `.symlink_to()` - Create symlink
- `.unbz()` - Unbz archive
- `.ungz()` - Ungz archive
- `.untar()` - Untar archive
- `.unxz()` - Unxz archive
- `.unzip()` - Unzip archive
- `.with_name()` - Rename file
- `.zip()` - Zip files
- `PathExtended(path)` - Constructor
- `PathExtended.tmp()` - Get temp directory/file
