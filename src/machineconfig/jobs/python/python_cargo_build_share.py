"""
cargo install
"""

# from machineconfig.utils.terminal import Terminal
# from machineconfig.utils.path_reduced import P as PathExtended
# import platform


# def build_rust_executable(url: str=r"https://github.com/atanunq/viu"):
#     tool_name = url.split('/')[-1]

#     # move command is not required since tool will go to .cargo/bin which is in PATH by default.
#     # move_command = f"mv {exe} {tb.get_env().WindowsApps.as_posix()}/" if platform.platform() == "Windows" else f"sudo mv {exe} /usr/local/bin/"
#     # {move_command}

#     script = f"""
# cd ~
# git clone --depth 1 {url}
# cd {tool_name}
# cargo install --path .
# """
#     print(f"""
# {'=' * 150}
# 🦀 CARGO BUILD | Building Rust project: {tool_name}
# 📦 Source: {url}
# {'=' * 150}
# """)
#     if platform.system() == "Windows":
#         Terminal(stdout=None).run(f". {PathExtended.tmpfile(suffix='.ps1').write_text(script, encoding="utf-8")}", shell="pwsh").print()
#     else:
#         Terminal(stdout=None).run(script, shell="pwsh")

#     exe = PathExtended.home().joinpath(f".cargo/bin/{tool_name}" + (".exe" if platform.system() == "Windows" else ""))

#     try:
#         PathExtended.home().joinpath(tool_name).delete(sure=True)
#     except PermissionError:
#         print(f"""
# {'⚠️' * 20}
# ⚠️  WARNING | Permission error when cleaning up
# 📂 Path: {PathExtended.home().joinpath(tool_name)}
# {'⚠️' * 20}
# """)

#     if platform.system() == "Windows":
#         exe = exe.move(folder=PathExtended.get_env().WindowsPaths().WindowsApps)
#     elif platform.system() in ["Linux", "Darwin"]:
#         Terminal().run(f"sudo mv {exe} /usr/local/bin")
#         exe = PathExtended(r"/usr/local/bin").joinpath(exe.name)
#     else:
#         raise NotImplementedError(f"🚫 Platform {platform.system()} not supported.")
#     share_link = exe.to_cloud("gdpo", share=True)
#     return share_link


# after cargo install diskonaut
# then mv ~/.cargo/bin/diskonaut.exe ~/AppData/Local/Microsoft/WindowsApps/
# then bu_gdrive_sx.ps1 .\diskonaut.exe -sRz  # zipping is vital to avoid security layers and keep file metadata.
