import shlex
import tempfile


def _kdl_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _build_cloud_tab_kdl(cloud_name: str, mount_cmd: str, mount_loc: str, focused: bool) -> str:
    focus_segment = " focus=true" if focused else ""
    escaped_cloud_name = _kdl_escape(cloud_name)
    escaped_mount_cmd = _kdl_escape(mount_cmd)
    escaped_mount_loc = _kdl_escape(mount_loc)
    escaped_about_target = _kdl_escape(f"{cloud_name}:")
    return f"""
    tab name=\"{escaped_cloud_name}\"{focus_segment} {{
        pane split_direction=\"vertical\" size=\"60%\" {{
            pane name=\"mount\" command=\"bash\" {{
                args \"-lc\" \"{escaped_mount_cmd}\"
            }}
            pane name=\"about\" command=\"rclone\" {{
                args \"about\" \"{escaped_about_target}\"
            }}
        }}
        pane split_direction=\"vertical\" size=\"40%\" {{
            pane name=\"explorer\" command=\"yazi\" {{
                args \"{escaped_mount_loc}\"
            }}
            pane name=\"monitor\" command=\"btm\" {{
                args \"--default_widget_type\" \"net\" \"--expanded\"
            }}
            pane name=\"shell\" cwd=\"{escaped_mount_loc}\"
        }}
    }}
"""


def _build_zellij_layout_kdl(mount_commands: dict[str, str], mount_locations: dict[str, str]) -> str:
    tab_blocks: list[str] = []
    for index, cloud_name in enumerate(mount_commands):
        tab_blocks.append(_build_cloud_tab_kdl(cloud_name=cloud_name, mount_cmd=mount_commands[cloud_name], mount_loc=mount_locations[cloud_name], focused=index == 0))
    return f"""layout {{
{''.join(tab_blocks)}
}}
"""


def get_within_current_session_code() -> str:
    return """

ZJ_SESSIONS=$(zellij list-sessions)

if [[ "${ZJ_SESSIONS}" != *"(current)"* ]]; then
    echo "Not inside a zellij session ..."
    echo '{mount_cmd} --daemon'
    # exit 1

    {mount_cmd} --daemon
fi

zellij run --direction down --name rclone -- {mount_cmd}
sleep 1; zellij action resize decrease down
sleep 0.2; zellij action resize decrease up
sleep 0.2; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
zellij run --direction right --name about -- rclone about {cloud}:
zellij action move-focus up
# zellij action write-chars "cd $HOME/data/rclone/{cloud}; sleep 0.1; ls"
zellij run --direction left --cwd $HOME/data/rclone/{cloud} -- yazi $HOME/data/rclone/{cloud}
zellij run --direction up -- btm --default_widget_type net --expanded
zellij run --in-place --cwd $HOME/data/rclone/{cloud} -- bash
zellij action move-focus up
"""


def build_zellij_launch_command(mount_commands: dict[str, str], mount_locations: dict[str, str], session_name: str) -> str:
    layout_kdl = _build_zellij_layout_kdl(mount_commands=mount_commands, mount_locations=mount_locations)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".kdl", prefix="cloud-mount-", delete=False) as layout_file:
        layout_file.write(layout_kdl)
        layout_path = layout_file.name
    return f"zellij --session {shlex.quote(session_name)} --new-session-with-layout {shlex.quote(layout_path)}"
