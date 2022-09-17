
croshell -c "from machineconfig.utils.utils import get_latest_release; f = get_latest_release(r'https://github.com/Genivia/ugrep').joinpath('ugrep.exe').download(); f.move(folder=f.get_env().WindowsApps, overwrite=True)"
