
# Non-login shells, .bashrc > .profile are read.
# for login shells, e.g. SSH, .bash_login > .bash_profile > .profile is read.

# The strategy to ensure consistent configuration for login and nonlogin shells is to put all the configuration in .bashrc, and then source it from .bash_profile and .profile.

# ensure .bash_profile only calls .profile
# ensure .profile calls .bashrc only at the end.

When you login: /etc/profile -> ~/.profile -> ~/.bash_profile -> ~/.bashrc
When you open a new terminal: ~/.bashrc
