
# LF (glang)
from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb

url = 'https://github.com/gokcehan/lf'

if __name__ == '__main__':
    tb.Terminal().run("nu -c 'ps | where name == lf.exe | each { |it| kill $it.pid --force}'", shell="pwsh").print()
    get_latest_release(url, file_name='lf-windows-amd64.zip', download_n_extract=True)
