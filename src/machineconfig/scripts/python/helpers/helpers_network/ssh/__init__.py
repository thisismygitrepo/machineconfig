from platform import system


def ssh_debug() -> dict[str, dict[str, str | bool]]:
    current_os = system()
    if current_os == "Linux":
        from machineconfig.scripts.python.helpers.helpers_network.ssh.ssh_debug_linux import ssh_debug_linux
        return ssh_debug_linux()
    elif current_os == "Darwin":
        from machineconfig.scripts.python.helpers.helpers_network.ssh.ssh_debug_darwin import ssh_debug_darwin
        return ssh_debug_darwin()
    elif current_os == "Windows":
        from machineconfig.scripts.python.helpers.helpers_network.ssh.ssh_debug_windows import ssh_debug_windows
        return ssh_debug_windows()
    else:
        raise NotImplementedError(f"ssh_debug is not supported on {current_os}")


__all__ = ["ssh_debug"]
