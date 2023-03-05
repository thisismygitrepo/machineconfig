

PROGRAM = """
# github.com/ajeetdsouza/zoxide#installation
echo "Installing zoxide must be done with non-admin privliage"
curl.exe -A "MS" https://webinstall.dev/zoxide | powershell
"""

def main(version=None):
    _ = version
    return PROGRAM


if __name__ == '__main__':
    main()

