"""Symlinks
"""

from machineconfig.utils.path_reduced import P as PathExtended
# from machineconfig.utils.utils import display_options


def main():
    print(f"""
{'=' * 150}
🔗 SYMLINK CREATOR | Create symlinks for virtual environments
{'=' * 150}
""")
    target = PathExtended(input("🎯 Symlink to which target? ")).expanduser().absolute()
    source = input(f"📍 Symlink from which source? [default to: CWD/{target.name}] ") or PathExtended.cwd().joinpath(target.name)
    if isinstance(source, str): source = PathExtended(source).expanduser().absolute()
    # ve_path = display_options(msg="symlin link? ", options=PathExtended.home().joinpath("ve").starget.symlink_to; PathExtended(r'$pwd').joinpath('venv').symlink_to(r'$to'); PathExtended('.gitignore').modify_text('venv', 'venv', replace_line=True)"(target.symlink_to(
    # PathExtended('.gitignore').modify_text('venv', 'venv', replace_line=True)"
    source.symlink_to(target, overwrite=True)
    print(f"""
{'=' * 150}
✅ SUCCESS | Symlink created successfully
📍 Source: {source}
🎯 Target: {target}
{'=' * 150}
""")
    return "echo '🔗 Finished creating symlink.'"


if __name__ == '__main__':
    pass
