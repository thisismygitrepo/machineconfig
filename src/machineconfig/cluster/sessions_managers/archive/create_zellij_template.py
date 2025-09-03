
"""ZT
"""

import socket
from machineconfig.utils.utils import choose_ssh_host, write_shell_script_to_default_program_path
from machineconfig.utils.path_reduced import P as PathExtended

prefix = """

layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children

}

"""

suffix = """

    tab name="THISMACHINE" focus=true // the default_tab_template
}
"""

tab = """

    tab name="TABNAME" focus=false { // the default_tab_template with three vertical panes between the plugins
        pane name="fpane" {
        command "TABCOMMAND"
        args "TABARGS"
        }
}

"""


def build_template(tabs: list[str]):
    res = prefix
    for t in tabs:
        res += tab.replace("TABNAME", t).replace("TABCOMMAND", "ssh").replace("TABARGS", t)
    res += suffix.replace("THISMACHINE", socket.gethostname())
    file = PathExtended.tmp().joinpath("tmp_files/templates/zellij_template.kdl")
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(res, encoding="utf-8")
    res = f"zellij --layout {file}"
    return res


def launch_from_ssh_config():
    hosts = choose_ssh_host(multi=True)
    assert isinstance(hosts, list)
    res = build_template(hosts)
    write_shell_script_to_default_program_path(res, execute=False, desc="zellij launch script", preserve_cwd=False, display=False)
    return None


if __name__ == '__main__':
    launch_from_ssh_config()
