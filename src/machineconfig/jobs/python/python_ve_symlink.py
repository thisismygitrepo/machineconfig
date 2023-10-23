
"""Symlinks
"""

import crocodile.toolbox as tb
# from machineconfig.utils.utils import display_options


def main():
    target = tb.P(input("Symlink to which target? ")).expanduser().absolute()
    source = input(f"symlink from which source ? [default to: CWD/{target.name}] ") or tb.P.cwd().joinpath(target.name)
    if isinstance(source, str): source = tb.P(source).expanduser().absolute()
    # ve_path = display_options(msg="symlin link? ", options=tb.P.home().joinpath("ve").starget.symlink_toimport crocodile.toolbox as tb; tb.P(r'$pwd').joinpath('venv').symlink_to(r'$to'); tb.P('.gitignore').modify_text('venv', 'venv', replace_line=True)"(target.symlink_to(
    # tb.P('.gitignore').modify_text('venv', 'venv', replace_line=True)"
    source.symlink_to(target, overwrite=True)
    return "echo '😁 Finished creating symlink.'"


if __name__ == '__main__':
    pass
