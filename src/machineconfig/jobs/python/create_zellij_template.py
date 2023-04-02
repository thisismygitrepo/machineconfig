
import crocodile.toolbox as tb
import socket
from machineconfig.utils.utils import display_options, write_shell_script

prefix = """

layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
           plugin location="zellij:status-bar"
        }
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


def build_template(tabs: list):
    res = prefix
    for t in tabs:
        res += tab.replace("TABNAME", t).replace("TABCOMMAND", f"ssh").replace("TABARGS", t)
    res += suffix.replace("THISMACHINE", socket.gethostname())
    file = tb.P.tmp().joinpath(f"tmp_files/templates/zellij_template.kdl").create(parents_only=True).write_text(res)
    res = f"zellij --layout {file}"
    return res


def launch_from_ssh_config():
    from paramiko import SSHConfig
    c = SSHConfig()
    c.parse(open(tb.P.home().joinpath(".ssh/config").str))
    choices = list(c.get_hostnames())
    hosts = display_options(msg="", options=choices, multi=True, fzf=True)
    res = build_template(hosts)
    # write_shell_script(res, execute=False, desc="zellij launch script")
    return c


if __name__ == '__main__':
    pass
