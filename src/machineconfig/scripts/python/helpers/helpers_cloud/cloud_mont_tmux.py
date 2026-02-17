import shlex


def build_tmux_launch_command(mount_commands: dict[str, str], mount_locations: dict[str, str], session_name: str) -> str:
    commands: list[str] = [f"tmux new-session -d -s {shlex.quote(session_name)}"]

    first_window = True
    for cloud_name, mount_cmd in mount_commands.items():
        window_target = f"{session_name}:{cloud_name}"
        mount_loc = mount_locations[cloud_name]

        mount_pane_cmd = f"bash -lc {shlex.quote(mount_cmd)}"
        about_pane_cmd = f"bash -lc {shlex.quote(f'rclone about {cloud_name}:; exec bash')}"
        explorer_pane_cmd = f"bash -lc {shlex.quote(f'yazi {shlex.quote(mount_loc)}')}"
        monitor_pane_cmd = f"bash -lc {shlex.quote('btm --default_widget_type net --expanded')}"
        shell_pane_cmd = f"bash -lc {shlex.quote(f'cd {shlex.quote(mount_loc)}; exec bash')}"

        if first_window:
            commands.append(f"tmux rename-window -t {shlex.quote(session_name)}:0 {shlex.quote(cloud_name)}")
            commands.append(f"tmux send-keys -t {shlex.quote(session_name)}:{shlex.quote(cloud_name)} {shlex.quote(mount_pane_cmd)} Enter")
            first_window = False
        else:
            commands.append(f"tmux new-window -t {shlex.quote(session_name)} -n {shlex.quote(cloud_name)} {shlex.quote(mount_pane_cmd)}")

        commands.append(f"tmux split-window -h -t {shlex.quote(window_target)} {shlex.quote(about_pane_cmd)}")
        commands.append(f"tmux select-pane -t {shlex.quote(window_target)}.0")
        commands.append(f"tmux split-window -v -t {shlex.quote(window_target)}.0 {shlex.quote(explorer_pane_cmd)}")
        commands.append(f"tmux select-pane -t {shlex.quote(window_target)}.1")
        commands.append(f"tmux split-window -v -t {shlex.quote(window_target)}.1 {shlex.quote(monitor_pane_cmd)}")
        commands.append(f"tmux select-pane -t {shlex.quote(window_target)}.2")
        commands.append(f"tmux split-window -v -t {shlex.quote(window_target)}.2 {shlex.quote(shell_pane_cmd)}")
        commands.append(f"tmux select-pane -t {shlex.quote(window_target)}.4")
        commands.append(f"tmux select-layout -t {shlex.quote(window_target)} tiled")

    commands.append(f"tmux attach-session -t {shlex.quote(session_name)}")
    return " ; ".join(commands)
