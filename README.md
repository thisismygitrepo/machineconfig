
# Welcome to machineconfig
Machineconfig is a package for managing configuration files (aka dotfiles). The idea is to collect those critical, time-consuming-files-to-setup in one directory and reference them via symbolic links from their original locations. Thus, when a new machine is to be setup, all that is required is to clone the repo in that machine and create the symbolic links.

Dotfiles include, but are not limited to:
* `~/.gitconfig`
* `~/.ssh`
* `~/.aws`
* `~/.bash_profile`
* `~/.bashrc`
* `~/.config`
* `$profile` in Windows Powershell
* etc

Additionally, files that contain data, sensitive information that should not be pushed to a repository are contained in a directory `~/dotfiles`. The files therein are encrypted before backedup.

Additionally, scripts to perform setup of new machines and perform mundane tasks are maintained here in `scripts`. The repo uses Python to perform the tasks.

## Windows Setup
With elevated `PowerShell`, run the following:
```ps1
# apps
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/blob/main/src/machineconfig/setup_windows/apps.ps1 | Invoke-Expression
# virtual enviornment
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/blob/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
# repos
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/blob/main/src/machineconfig/symlinks/repos.ps1 | Invoke-Expression
# symlinks
~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1
# devapps:
~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1
```

###### Install Croshell Terminal Directly,
```ps1
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/src/machineconfig/setup_windows/croshell.ps1 | Invoke-Expression
```

###### Setup SSH connection:
```ps1
# Remotely without connection:
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/blob/main/src/machineconfig/setup_windows/openssh-server.ps1 | Invoke-Expression
# Locally:
~/machineconfig/src/machineconfig/setup_windows/openssh-server_copy-ssh-id.ps1 | Invoke-Expression
# On the remote via password-based connection:
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/blob/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1 | Invoke-Expression
```

# Linux Setup
