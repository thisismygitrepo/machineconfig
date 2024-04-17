
"""
natural language to API
https://github.com/ShishirPatil/gorilla
"""

from machineconfig.utils.ve import get_ve_install_script
# import subprocess

ve_name = "goex"
install_script = get_ve_install_script(ve_name=ve_name, py_version="3.11", install_crocodile_and_machineconfig=False,
                                       delete_if_exists=True, system=None)


install_script += f"""

. activate_ve {ve_name}
cd ~/code/foreign
git clone https://github.com/ShishirPatil/gorilla --depth 1
cd gorilla/goex
pip install -e .

"""
