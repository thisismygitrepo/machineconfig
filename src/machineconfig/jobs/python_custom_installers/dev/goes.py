
"""
natural language to API
https://github.com/ShishirPatil/gorilla
"""

from machineconfig.utils.ve import get_ve_install_script
# import subprocess

config_dict = {
        "repo_url": "CUSTOM",
        "doc": "natural language to API",
        "filename_template_windows_amd_64": "",
        "filename_template_linux_amd_64": "",
        "strip_v": False,
        "exe_name": "goex"
    }

ve_name = "goex"


def main():
    install_script = get_ve_install_script(ve_name=ve_name, py_version="3.11", install_crocodile_and_machineconfig=False,
                                        delete_if_exists=True)


    install_script += f"""

. $HOME/scripts/activate_ve {ve_name}
cd ~/code/foreign
git clone https://github.com/ShishirPatil/gorilla --depth 1
cd gorilla/goex
pip install -e .

    """
    return install_script


if __name__ == "__main__":
    pass
