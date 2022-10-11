
# fzf (glang)
# search for files/folder names, but can come with preview option. For that use: my variant fzz.ps1
from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb
tb.Terminal().run('nu -c "ps | where name == fzf.exe | each { |it| kill `$it.pid --force}"', shell="pwsh")
get_latest_release('https://github.com/junegunn/fzf', suffix='windows_amd64', download_n_extract=True)

