
<p align="center">

<a href="https://github.com/thisismygitrepo/machineconfig/commits">
<img src="https://img.shields.io/github/commit-activity/m/thisismygitrepo/machineconfig" />
</a>

</p>


# Welcome to machineconfig

Machineconfig is a package for managing configuration files (aka dotfiles). The idea is to collect those critical, time-consuming-files-to-setup in one directory and reference them via symbolic links from their original locations. Thus, when a new machine is to be setup, all that is required is to clone the repo in that machine and create the symbolic links.
Dotfiles are divided into private and public. Examples of private ones are, `~/.gitconfig`, `~/.ssh`, etc. Whereas public config files are ones like `lfrc`. The private dotfiles are placed @ `~/dotfiles`. The files therein are encrypted before backedup.

# Install On Windows:

```powershell
# install tool the tool only:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"  # Skip if UV is already installed
uv tool install --upgrade --python 3.14 machineconfig
# interactive install of machineconfig and following on to run it and make basic machine configuration (RECOMMENDED):
iex (iwr bit.ly/cfgwindows).Content  # Or, if UV is installed: iex (uvx machineconfig define)
# Quick install and configure (optionals are accepted by default):
iex (iwr bit.ly/cfgwq).Content
```

# Install On Linux and MacOS

```bash
# install tool the tool only:
curl -LsSf https://astral.sh/uv/install.sh | sh  # Skip if UV is already installed
uv tool install --upgrade --python 3.14 machineconfig
# interactive install of machineconfig and following on to run it and make basic machine configuration (RECOMMENDED):
. <(curl -L bit.ly/cfglinux) # Or, if UV is installed: . <(uvx machineconfig define)
```


# Author
Alex Al-Saffar. [email](mailto:programmer@usa.com)

# Contributor
Ruby Chan. [email](mailto:ruby.chan@sa.gov.au)


[![Alex's github activity graph](https://github-readme-activity-graph.vercel.app/graph?username=thisismygitrepo)](https://github.com/ashutosh00710/github-readme-activity-graph)

