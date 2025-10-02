
<p align="center">

<a href="https://github.com/thisismygitrepo/machineconfig/commits">
<img src="https://img.shields.io/github/commit-activity/m/thisismygitrepo/machineconfig" />
</a>

</p>


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


# Windows:

```powershell
iex (iwr bit.ly/cfgiawindows).Content
```

# Linux and MacOS

```bash
. <(curl -sL bit.ly/cfgialinux)
```


# Author
Alex Al-Saffar. [email](mailto:programmer@usa.com)

[![Alex's github activity graph](https://github-readme-activity-graph.vercel.app/graph?username=thisismygitrepo)](https://github.com/ashutosh00710/github-readme-activity-graph)

