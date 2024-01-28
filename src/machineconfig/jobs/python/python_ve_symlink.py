
"""Symlinks
"""

from crocodile.file_management import P
# from machineconfig.utils.utils import display_options


def main():
    target = P(input("Symlink to which target? ")).expanduser().absolute()
    source = input(f"symlink from which source ? [default to: CWD/{target.name}] ") or P.cwd().joinpath(target.name)
    if isinstance(source, str): source = P(source).expanduser().absolute()
    # ve_path = display_options(msg="symlin link? ", options=P.home().joinpath("ve").starget.symlink_to; P(r'$pwd').joinpath('venv').symlink_to(r'$to'); P('.gitignore').modify_text('venv', 'venv', replace_line=True)"(target.symlink_to(
    # P('.gitignore').modify_text('venv', 'venv', replace_line=True)"
    source.symlink_to(target, overwrite=True)
    return "echo '😁 Finished creating symlink.'"


if __name__ == '__main__':
    pass
