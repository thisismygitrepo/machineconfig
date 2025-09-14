# """DS
# """


# from machineconfig.cluster.remote_machine import RemoteMachine, FileManager


# class Submission:
#     """Sends repo, data, root_dir and write execution command."""
#     @staticmethod
#     def transfer_sh(rm: RemoteMachine) -> None:
#         print("🚀 Using transfer.sh to send data to remote machine.")
#         cloud_download_py_script = "\n"
#         # downloading repo, this takes place prior to pyscript (otherwise, its tool late as the library is loaded at the top of the pyscript already)
#         if rm.config.copy_repo:
#             tmp_file = PathExtended(rm.job_params.repo_path_rh).expanduser().zip_n_encrypt()
#             cloud_download_py_script += f"print('Downloading `{tmp_file.collapseuser()}`.')\n"
#             cloud_download_py_script += f"P(r'{tmp_file.share_on_cloud()}').download(folder=r'{P(rm.job_params.repo_path_rh).parent}').decrypt_n_unzip()\n"
#             tmp_file.delete(sure=True)
#         for _idx, item in enumerate(rm.data):
#             cloud_download_py_script += f"P(r'{P(item).share_on_cloud()}').download(folder=r'{item.collapseuser().parent}')\n"
#         # save cloud_download_script_py
#         rm.file_manager.cloud_download_py_script_path.expanduser().write_text(cloud_download_py_script, encoding="utf-8")
#         # modify and save shell_script to including running of cloud_download_py_script before job script.
#         shell_file = rm.file_manager.shell_script_path.expanduser()
#         shell_script = shell_file.read_text(encoding="utf-8").replace("# EXTRA-PLACEHOLDER-POST", f"cd ~; python {rm.file_manager.cloud_download_py_script_path.rel2home().as_posix()}")
#         download_url = rm.file_manager.job_root.zip().share_on_cloud()
#         target = rm.file_manager.job_root.rel2home().parent.joinpath(download_url.name).as_posix()
#         tmp = f"cd ~; curl -o '{target}' '{download_url.as_url_str()}'; unzip '{target}' -d {rm.file_manager.job_root.rel2home().parent.as_posix()}"
#         shell_script = tmp + shell_script
#         with open(file=shell_file, mode='w', newline={"Windows": None, "Linux": "\n"}[rm.ssh.get_remote_machine()], encoding="utf-8") as file: file.write(shell_script)

#     @staticmethod
#     def cloud(rm: RemoteMachine) -> None:
#         cloud = rm.config.cloud_name
#         assert cloud is not None, "Cloud name is not specified in the config file. Please specify it in the config file."
#         if rm.config.copy_repo: PathExtended(rm.job_params.repo_path_rh).to_cloud(cloud=cloud, rel2home=True, zip=True, encrypt=True)
#         for x in rm.data: x.to_cloud(cloud=cloud, rel2home=True)
#         downloads = '\n'.join([f"cloud_copy {cloud}: '{a_path.collapseuser().as_posix()} -r" for a_path in rm.data])
#         if not rm.config.copy_repo: downloads += f"""\n cloud_copy {cloud}: {P(rm.job_params.repo_path_rh).collapseuser().as_posix()} -zer """
#         downloads += f"\ncloud_copy {cloud}: {rm.file_manager.job_root} -zr"
#         rm.file_manager.shell_script_path.expanduser().write_text(downloads + rm.file_manager.shell_script_path.expanduser().read_text(encoding="utf-8"), encoding='utf-8')  # newline={"Windows": None, "Linux": "\n"}[rm.ssh.get_remote_machine()]
#         PathExtended(rm.file_manager.job_root).to_cloud(cloud=cloud, zip=True, rel2home=True)

#     @staticmethod
#     def sftp(rm: RemoteMachine) -> None:
#         assert rm.ssh.sftp is not None, f"SFTP is not available for this machine `{rm.ssh}`. Consider using different `transfer_method` other than `sftp`."
#         log_path_parent = f"P(r'{FileManager.shell_script_path_log}').expanduser().parent"
#         rm.ssh.run_py(f"{log_path_parent}.mkdir(parents=True, exist_ok=True); P(r'{FileManager.shell_script_path_log}').expanduser().delete(sure=True).write_text(r'{rm.file_manager.shell_script_path.collapseuser().as_posix()}')", desc="Logging latest shell script path on remote.", verbose=False)
#         if rm.config.copy_repo: rm.ssh.copy_from_here(rm.job_params.repo_path_rh, z=True, overwrite=True)
#         for a_path in rm.data:
#             rm.ssh.copy_from_here(
#                 a_path,
#                 z=True if PathExtended(a_path).is_dir() else False,
#                 r=False,
#                 overwrite=True,
#             )
#         rm.ssh.copy_from_here(rm.file_manager.job_root, z=True)


# if __name__ == '__main__':
#     pass
