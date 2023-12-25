
from typing import Optional

__doc__ = """A cd command that learns - easily navigate directories from the command-line"""


PROGRAM = """
# github.com/ajeetdsouza/zoxide#installation
echo "Installing zoxide must be done with non-admin privliage"
curl.exe -A "MS" https://webinstall.dev/zoxide | powershell
"""


def main(version: Optional[str] = None):
    _ = version
    return PROGRAM


if __name__ == '__main__':
    main()
