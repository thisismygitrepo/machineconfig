
from typing import Optional


__doc__ = """Azure Data Studio is a data management tool that enables working with SQL Server, Azure SQL DB and SQL DW from Windows, macOS and Linux."""


def main(version: Optional[str] = None):
    _ = version
    return f"""

curl https://azuredatastudio-update.azurewebsites.net/latest/linux-x64/stable -o ~/azuredatastudio-linux-x64.tar.gz
tar -xvf ~/azuredatastudio-linux-<version string>.tar.gz
echo 'export PATH="$PATH:~/azuredatastudio-linux-x64"' >> ~/.bashrc
source ~/.bashrc

"""


if __name__ == '__main__':
    main()
