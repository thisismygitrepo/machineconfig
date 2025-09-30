# """Run with sane defaults for a remote machine.
# """

# from machineconfig.cluster.remote_machine import RemoteMachine, RemoteMachineConfig
# from machineconfig.cluster.cloud_manager import CloudManager
# from machineconfig.cluster.loader_runner import WorkloadParams
# from machineconfig.cluster.self_ssh import SelfSSH
# from machineconfig.utils.utils import DEFAULTS_PATH
# from machineconfig.utils.utils2 import read_ini
# from typing import Any, Callable, Union

# _ = WorkloadParams


# try:
#     section = read_ini(DEFAULTS_PATH)['general']
#     to_email_default = section['to_email']
#     email_config_name_default = section['email_config_name']
# except (FileNotFoundError, KeyError, IndexError):
#     to_email_default = 'random@email.com'
#     email_config_name_default = 'enaut'

# try: default_cloud: str = read_ini(DEFAULTS_PATH)['general']['rclone_config_name']
# except (FileNotFoundError, KeyError, IndexError): default_cloud = 'gdrive'


# def run_on_cloud(func: Union[str, Callable[[WorkloadParams], Any]], split: int, reset_cloud: bool = False, reset_local: bool = False):
#     if hasattr(func, '__doc__'): description = str(func.__doc__)
#     else: description = "Description of running an expensive function"
#     config = RemoteMachineConfig(
#         # connection
#         ssh_obj=SelfSSH(),  # overrides ssh_params
#         description=description,  # job_id=, base_dir="",
#         # data
#         copy_repo=False, update_repo=True, install_repo=False, update_essential_repos=True, data=[], transfer_method="cloud", cloud_name=email_config_name_default,
#         # remote machine behaviour
#         open_console=True, notify_upon_completion=True, to_email=to_email_default, email_config_name=email_config_name_default,
#         kill_on_completion=True,
#         launch_method="cloud_manager",
#         # execution behaviour
#         ipython=False, interactive=False, pdb=False, pudb=False, wrap_in_try_except=True,
#         workload_params=None,  # to be added later per sub-job.
#         # resources
#         lock_resources=False, max_simulataneous_jobs=2, parallelize=False, )
#     m = RemoteMachine(func=func, func_kwargs=None, config=config)
#     res = m.submit_to_cloud(split=split, cm=CloudManager(max_jobs=0, reset_local=reset_local), reset_cloud=reset_cloud)
#     return res


# if __name__ == "__main__":
#     pass
