"""Symlinks"""

from machineconfig.utils.path_reduced import PathExtended as PathExtended
# from machineconfig.utils.utils import display_options


def main():
    print(f"""
{"=" * 150}
🔗 SYMLINK CREATOR | Create symlinks for virtual environments
{"=" * 150}
""")
    target = PathExtended(input("🎯 Symlink to which target? ")).expanduser().absolute()
    source = input(f"📍 Symlink from which source? [default to: CWD/{target.name}] ") or PathExtended.cwd().joinpath(target.name)
    if isinstance(source, str):
        source = PathExtended(source).expanduser().absolute()
    source.symlink_to(target, overwrite=True)
    print(f"""
{"=" * 150}
✅ SUCCESS | Symlink created successfully
📍 Source: {source}
🎯 Target: {target}
{"=" * 150}
""")
    print("🔗 Finished creating symlink.")


if __name__ == "__main__":
    pass
