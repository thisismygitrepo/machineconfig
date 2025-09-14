# """Trogon
# """

# #
# # from machineconfig.cluster.distribute import Cluster, WorkloadParams
# from machineconfig.cluster.remote_machine import RemoteMachineConfig, RemoteMachine, CloudManager
# from machineconfig.cluster.templates.run_cloud import to_email_default, email_config_name_default, default_cloud
# import click
# # from trogon import tui
# from typing import Any, Optional


# @click.command()
# @click.option('--file', prompt="Py File: ", help="The file to run.", default="")
# @click.option('--function', prompt="Function: ", help="The function to run.", default=None)
# @click.pass_context
# def main2(ctx: Any, file: str, function: Optional[str] = None):
#     ctx.obj = {'file': file, 'function': function}


# # @tui()
# # @click.group("gg")
# @click.command()
# @click.option('--file', prompt="Py File: ", help="The file to run.", default="")
# @click.option('--function', prompt="Function: ", help="The function to run.", default=None)
# @click.option('--description', prompt="Description of the job: ", default=f"Description of running func on remotes", help="Write something that describes what this job is about.")
# @click.option('--update_repo', prompt="Update repo: ", default=False, help="Update the repo on the remote machine.")
# @click.option('--update_essential_repos', prompt="Update essential repos: ", default=True, help="Update essential repos on the remote machine.")
# @click.option('--cloud_name', prompt="Cloud name: ", default=default_cloud, help="The name of the cloud to use.")
# @click.option('--notify_upon_completion', prompt="Notify upon completion: ", default=False, help="Send an email upon completion.")
# @click.option('--to_email', prompt="To email: ", default=to_email_default, help="The email to send to.")
# @click.option('--email_config_name', prompt="Email config name: ", default=email_config_name_default, help="The name of the email config to use.")
# @click.option('--kill_on_completion', prompt="Kill on completion: ", default=False)
# @click.option('--ipython', prompt="Use ipython: ", default=False)
# @click.option('--interactive', prompt="Interactive: ", default=False)
# @click.option('--pdb', prompt="Use pdb: ", default=False)
# @click.option('--pudb', prompt="Use pudb: ", default=False)
# @click.option('--wrap_in_try_except', prompt="Wrap in try except: ", default=False)
# @click.option('--lock_resources', prompt="Lock resources: ", default=False)
# @click.option('--max_simulataneous_jobs', prompt="Max simultaneous jobs: ", default=2)
# @click.option('--split', prompt="Split: ", default=1)
# @click.option('--reset_cloud', prompt="Reset cloud: ", default=False)
# @click.option('--reset_local', prompt="Reset local: ", default=False)
# # @click.pass_context
# def main(
#          file: str, function: Optional[str],
#          description: str, update_repo: bool, update_essential_repos: bool, cloud_name: str,
#          notify_upon_completion: bool, to_email: str, email_config_name: str, kill_on_completion: bool, ipython: bool, interactive: bool,
#          pdb: bool, pudb: bool, wrap_in_try_except: bool, lock_resources: bool, max_simulataneous_jobs: bool,
#          split: int, reset_cloud: bool, reset_local: bool,
#           ) -> Any:

#     # function = ctx.obj['function']
#     # description = ctx.obj['file']
#     from machineconfig.cluster.self_ssh import SelfSSH
#     config = RemoteMachineConfig(
#         # connection
#         ssh_obj=SelfSSH(),
#         # ssh_params=None,
#         description=description,
#         # job_id=, base_dir="",
#         # data
#         copy_repo=False,  # copy_repo,
#         update_repo=update_repo,
#         install_repo=True,  # install_repo,
#         update_essential_repos=update_essential_repos,
#         data=[],
#         transfer_method="cloud",  # "transfer_method,
#         cloud_name=cloud_name,
#         # remote machine behaviour
#         # open_console=open_console,
#         notify_upon_completion=notify_upon_completion,
#         to_email=to_email,
#         email_config_name=email_config_name,
#         kill_on_completion=kill_on_completion,
#         workload_params=None,
#         launch_method="cloud_manager",
#         # execution behaviour
#         ipython=ipython,
#         interactive=interactive,
#         pdb=pdb,
#         pudb=pudb,
#         wrap_in_try_except=wrap_in_try_except,
#         # resources
#         lock_resources=lock_resources,
#         max_simulataneous_jobs=max_simulataneous_jobs,
#         parallelize=False,  # parallelize,
#     )

#     if function is not None:
#         module: dict[str, Any] = Read.py(file)
#         func = module[function]
#     else: func = file
#     m = RemoteMachine(func=func, func_kwargs=None, config=config)
#     res = m.submit_to_cloud(split=split, cm=CloudManager(max_jobs=0, reset_local=reset_local), reset_cloud=reset_cloud)
#     return res


# if __name__ == '__main__':
#     # conf = get_options(standalone_mode=False)  # type: ignore  # pylint: disable=no-value-for-parameter
#     # main2()  # type: ignore
#     main()  # type: ignore
