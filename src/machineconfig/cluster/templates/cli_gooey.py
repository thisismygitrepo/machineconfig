# """Gooey
# """

# from argparse import ArgumentParser
# # from gooey import Gooey  #, GooeyParser
# # from machineconfig.cluster.distribute import Cluster, WorkloadParams
# from machineconfig.cluster.remote_machine import RemoteMachineConfig
# # from machineconfig.cluster.utils import expensive_function
# from machineconfig.utils.utils import DEFAULTS_PATH
# from machineconfig.utils.utils2 import read_ini
# # from typing import Any, Optional


# @Gooey(program_name="Cluster Launcher", program_description='Cofigure remote cluster and launch jobs.')  # type: ignore
# def main() -> RemoteMachineConfig:
#     # parser = GooeyParser(description='Example of Gooey\'s basic functionality')
#     parser = ArgumentParser(description='Cluster Launcher')
#     from machineconfig.scripts.python.cloud_mount import get_rclone_config
#     cloud_names = get_rclone_config().sections()
#     #     job_id=, base_dir="",
#     parser.add_argument('Description', help='The file you want to process', default="Description of running func on remotes")

#     # # execution behaviour
#     # wrap_in_try_except=True
#     parser.add_argument('-w', '--wrap_in_try_except', help='Wrap in try except', action='store_true', default=False)
#     # pudb=False
#     parser.add_argument('-p', '--pudb', help='Use pudb', action='store_true', default=False)
#     # pdb=False
#     parser.add_argument('-d', '--pdb', help='Use pdb', action='store_true', default=False)
#     # interactive=True
#     parser.add_argument('-i', '--interactive', help='Interactive', action='store_true', default=False)
#     # ipython=True
#     parser.add_argument('-y', '--ipython', help='Use ipython', action='store_true', default=False)

#     # # resources
#     # lock_resources=True
#     parser.add_argument('-l', '--lock_resources', help='Lock resources', action='store_true', default=False)
#     # max_simulataneous_jobs=2
#     parser.add_argument('-m', '--max_simulataneous_jobs', help='Max simultaneous jobs', type=int, default=2)
#     # parallelize=False
#     # parser.add_argument('-a', '--parallelize', help='Parallelize', action='store_true', default=False)

#     # # data
#     # copy_repo = True
#     # parser.add_argument('-c', '--copy_repo', help='Copy repo', action='store_true', default=True)
#     # update_repo=False
#     parser.add_argument('-u', '--update_repo', help='Update repo', action='store_true', default=False)
#     # install_repo=False
#     # parser.add_argument('-n', '--install_repo', help='Install repo', action='store_true', default=False)
#     # update_essential_repos=True
#     parser.add_argument('-e', '--update_essential_repos', help='Update essential repos', action='store_true', default=True)
#     # transfer_method="sftp"
#     # parser.add_argument('-t', '--transfer_method', help='Transfer method', choices=['sftp', 'cloud'], default='sftp')
#     # open_console=True
#     # parser.add_argument('-o', '--open_console', help='Open console', action='store_true', default=True)

#     # # remote machine behaviour
#     parser.add_argument('cloud_name', help='Cloud Rclone Config Name', default="oduq1", choices=cloud_names)
#     parser.add_argument('-v', '--notify_upon_completion', help='Notify upon completion', action='store_true', default=True)

#     try:
#         section = read_ini(DEFAULTS_PATH)['general']
#         to_email = section['to_email']
#         email_config_name = section['email_config_name']
#     except (FileNotFoundError, KeyError, IndexError):
#         to_email = 'random@email.com'
#         email_config_name = 'enaut'

#     parser.add_argument('-z', '--to_email', help='To email', default=to_email)
#     parser.add_argument('-f', '--email_config_name', help='Email config name', default=email_config_name)
#     parser.add_argument('-k', '--kill_on_completion', help='Kill terminal tab/pane for this job on completion', action='store_true', default=False)
#     parser.add_argument('split', help='How many jobs to split into', type=int, default=3)

#     # https://github.com/chriskiehl/GooeyExamples/blob/master/examples/FilterableDropdown.py
#     args = parser.parse_args()

#     from machineconfig.cluster.self_ssh import SelfSSH
#     config = RemoteMachineConfig(
#         # connection
#         ssh_obj=SelfSSH(),
#         # ssh_params=None,
#         description=args.Description,
#         # job_id=, base_dir="",
#         # data
#         copy_repo=False,  # args.copy_repo,
#         update_repo=args.update_repo,
#         install_repo=True,  # args.install_repo,
#         update_essential_repos=args.update_essential_repos,
#         data=[],
#         transfer_method="cloud",  # "args.transfer_method,
#         cloud_name=args.cloud_name,
#         # remote machine behaviour
#         # open_console=args.open_console,
#         notify_upon_completion=args.notify_upon_completion,
#         to_email=args.to_email,
#         email_config_name=args.email_config_name,
#         kill_on_completion=args.kill_on_completion,
#         workload_params=None,
#         launch_method="cloud_manager",
#         # execution behaviour
#         ipython=args.ipython,
#         interactive=args.interactive,
#         pdb=args.pdb,
#         pudb=args.pudb,
#         wrap_in_try_except=args.wrap_in_try_except,
#         # resources
#         lock_resources=args.lock_resources,
#         max_simulataneous_jobs=args.max_simulataneous_jobs,
#         parallelize=False,  # args.parallelize,
#     )
#     return config


# if __name__ == '__main__':
#     main()
