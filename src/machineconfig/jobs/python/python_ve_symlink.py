"""Symlinks
"""

from crocodile.file_management import P
# from machineconfig.utils.utils import display_options


def main():
    print(f"""
{'=' * 70}
🔗 SYMLINK CREATOR | Create symlinks for virtual environments
{'=' * 70}
""")
    target = P(input("🎯 Symlink to which target? ")).expanduser().absolute()
    source = input(f"📍 Symlink from which source? [default to: CWD/{target.name}] ") or P.cwd().joinpath(target.name)
    if isinstance(source, str): source = P(source).expanduser().absolute()
    # ve_path = display_options(msg="symlin link? ", options=P.home().joinpath("ve").starget.symlink_to; P(r'$pwd').joinpath('venv').symlink_to(r'$to'); P('.gitignore').modify_text('venv', 'venv', replace_line=True)"(target.symlink_to(
    # P('.gitignore').modify_text('venv', 'venv', replace_line=True)"
    source.symlink_to(target, overwrite=True)
    print(f"""
{'=' * 70}
✅ SUCCESS | Symlink created successfully
📍 Source: {source}
🎯 Target: {target}
{'=' * 70}
""")
    return "echo '🔗 Finished creating symlink.'"


if __name__ == '__main__':
    pass
