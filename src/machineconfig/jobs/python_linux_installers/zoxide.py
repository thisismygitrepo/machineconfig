
from machineconfig.utils.installer import get_latest_release
import platform
from typing import Optional
from crocodile.toolbox import P


repo_url = "https://github.com/ajeetdsouza/zoxide/"
__doc__ = """forget about cd ls"""
# although there are installers, howwever, they are finiky about priviliage and cause troubles.


def main(version: Optional[str] = None):
    # if platform.system() == "Windows":
    #     release = get_latest_release(repo_url=repo_url, exe_name="zoxide", version=version, download_n_extract=False)
    #     if not isinstance(release, P):
    #         print(f"Could not find zellij release for version {version}")
    #         return None
    #     find_move_delete_windows(downloaded=release.joinpath("ttyd.win32.exe").download().with_name("ttyd.exe", inplace=True), tool_name="ttyd.exe")
    if platform.system() == "Linux":
        release = get_latest_release(repo_url=repo_url, exe_name="zoxide", version=version, download_n_extract=False)
        if not isinstance(release, P):
            print(f"Could not find zellij release for version {version}")
            return None
        deb_file = release.joinpath(f"zoxide_{release.name.strip('v')}_amd64.deb").download()
        install_bash_program = f"""
sudo dpkg -i {deb_file}
rm {deb_file}
# (echo 'eval "$(zoxide init bash)"' >> ~/.bashrc) || true
"""
        from machineconfig.utils.utils import write_shell_script
        write_shell_script(program=install_bash_program, display=True, preserve_cwd=True, desc="Shell script prepared by Python.", execute=True)
        return ""


if __name__ == '__main__':
    main()
