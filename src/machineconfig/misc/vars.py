
"""
Variables:
There exist enviroment variables and then there are shell variables. Distinciton in mind is due.
A shell variable is abailable in that shell session and other programs are not aware of it.
An enviroment variable is abailable to all programs running on the system.

Shell variables can live for the lifetime of the shell itself, unless they are reloaded again from
the configuration script. Enviroment variables live forever, unless explicitly removed.

Enviroment variables can only be strings. Shell variables can be anything.

Shell vars are not inherited by subprocess launched from the shell at hand.

Path, is a special enviroment variable. It contains directories that will be searched when looking
for executables. If you have an executable, it is not recommended to put its path as an inviroment variable.
Otherwise, you need to give it a name and then explicitly launch it with, .e.g `start $julia`
The correct way to do it is to add its directory to its Path.

Acecss enviroemtn variable:
    Linux: `env`
    Windows: dir env: OR gci env:  where both gci and dir are aliases in PS for Get-ChildItem

Thus, PATH, being special, but not so much different from any other enviroment variables is acessed this way:
    Linxu: $PATH (in linux, there is no distinction between enviroment and shell variable access, both use $name)
    Windows: $env:Path (Windows separates enviroment variables from shell by prefix $env:name vs $name )

PAckage that I did not realize whats the point of them
https://github.com/theskumar/python-dotenv
https://pypi.org/project/python-decouple/
https://github.com/sloria/environs

"""


if __name__ == '__main__':
    pass
