

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb


def main():
    find_move_delete_linux(downloaded=tb.P("https://ranger.github.io/ranger-stable.tar.gz").download().ungz_untar(), tool_name="ranger")

    return ""


if __name__ == '__main__':
    main()
