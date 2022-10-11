
# LF (glang)
from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb
tb.Terminal().run('nu -c "ps | where name == lf.exe | each { |it| kill `$it.pid --force}"', shell="pwsh")
get_latest_release('https://github.com/gokcehan/lf', name='lf-windows-amd64.zip', download_n_extract=True)
