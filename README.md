
<p align="center">

<a href="https://github.com/thisismygitrepo/machineconfig/commits">
<img src="https://img.shields.io/github/commit-activity/m/thisismygitrepo/machineconfig" />
</a>

</p>


# Welcome to machineconfig

# Shortcuts
* `bit.ly/cfgroot` is a shortcut to this repo.
* `glow https://bit.ly/cfgread` OR `curl bit.ly/cfgread -L | bat -l md --style="header"` to get the readme file.

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


## Windows Setup
With elevated `PowerShell`, run the following: (short `curl bit.ly/cfgallwindows -L | iex`)

**You have to have `winget` first. If its not available in the your terminal, try those resources:**

* https://github.com/asheroto/winget-install
* https://github.com/microsoft/winget-cli
* https://github.com/microsoft/winget-cli/discussions/3258


```shell
# apps  # short: `(iwr bit.ly/cfgappswindows).Content | iex`
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/apps.ps1 | Invoke-Expression
# virtual enviornment  # short (iwr bit.ly/cfgvewindows).Content | iex OR `curl bit.ly/cfgvewindows -L | iex`
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
# symlinks # short `(iwr bit.ly/cfgsymlinkswindows).Content | iex` OR `curl bit.ly/cfgsymlinkswindows -L | iex`
. $HOME/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1
# devapps:
$HOME/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1
# pwsh and wt settings: (iwr bit.ly/cfgwt).Content | iex
iwr https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/wt_and_pwsh.ps1 | iex

```

```shell

(iwr bit.ly/cfgappswindows).Content | iex
(iwr bit.ly/cfgvewindows).Content | iex
. $HOME/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1
(iwr bit.ly/cfgwt).Content | iex
. $HOME/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1

& "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"
python -m fire machineconfig.profile.create main2 --choice=all
deactivate

```

###### Setup SSH connection:
```shell
# CHANGE pubkey_string APPROPRIATELY
$pubkey_string=(Invoke-WebRequest 'https://github.com/thisismygitrepo.keys').Content
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression
```
short `(iwr bit.ly/cfgsshwindows).Content | iex` OR `curl bit.ly/cfgsshwindows -L | iex`

###### Install Croshell Terminal Directly,
```shell
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/web_shortcuts/croshell.ps1 | Invoke-Expression
```
short: `curl bit.ly/cfgcroshellwindows -L | iex` OR `(iwr bit.ly/cfgcroshellwindows).Content | iex`


# Linux Setup
With `sudo` access, run the following: (short `curl bit.ly/cfgalllinux -L | bash`)
```bash
export package_manager="nala"
export package_manager="nix"

# apps  # short: `curl bit.ly/cfgappslinux -L | bash`
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps.sh | bash
# Optionally: curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps_dev.sh | bash

# virtual enviornment  # short `curl bit.ly/cfgvelinux -L | bash`
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash

# repos  # short `curl bit.ly/cfgreposlinux -L | bash`
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash
# symlinks and bash profile: # short `curl bit.ly/cfgsymlinkslinux -L | bash`
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh  # requires sudo since it invloves chmod of dotfiles/.ssh, however sudo doesn't work with source. best to have sudo -s earlier.

# devapps
source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)
```

###### Setup SSH connection:
```bash
pubkey_url='https://github.com/thisismygitrepo.keys'  # (CHANGE APPROPRIATELY)
export pubkey_string=$(curl --silent $pubkey_url)
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash
# For WSL only, also run the following:
export port=2223
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash
# don't forget to run `wsl_ssh_windows_port_forwarding -p 2223` from Windows using the designated port with
```
short `curl bit.ly/cfgsshlinux -L | bash`


###### Install Croshell Terminal Directly

```bash

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/web_shortcuts/croshell.sh | sudo bash

```
short `curl bit.ly/cfgcroshelllinux -L | bash`


# Author
Alex Al-Saffar. [email](mailto:programmer@usa.com)

[![Alex's github activity graph](https://github-readme-activity-graph.vercel.app/graph?username=thisismygitrepo)](https://github.com/ashutosh00710/github-readme-activity-graph)

