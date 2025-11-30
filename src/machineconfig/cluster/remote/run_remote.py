# """
# This file contains a template for a remote machine. It is not meant to be run, but rather to be used as a template for
# """


# def run_on_remote():
#     from machineconfig.cluster.remote_machine import RemoteMachine, RemoteMachineConfig, WorkloadParams
#     from machineconfig.cluster.templates.utils import expensive_function
#     # from machineconfig.cluster.self_ssh import SelfSSH
#     data: list[Path] = []
#     config = RemoteMachineConfig(
#         # connection
#         #        ssh_obj=SelfSSH(),  # overrides ssh_params
#         ssh_params=dict(host="ts"),  # dict(host="239wsl"),
#         description="Description of running an expensive function",  # job_id=, base_dir="",
#         # data
#         copy_repo=False, update_repo=True, install_repo=False, update_essential_repos=True, data=data, transfer_method="sftp",
#         # remote machine behaviour
#         open_console=True, notify_upon_completion=True, to_email=None, email_config_name=None, kill_on_completion=False,
#         # execution behaviour
#         ipython=True, interactive=True, pdb=False, pudb=False, wrap_in_try_except=True,
#         workload_params=None,  # this means no workload params object will be created in execution script, nor fed explicitil with workload_params=workload_params.
#         # resources
#         lock_resources=True, max_simulataneous_jobs=2, parallelize=False, )
#     m = RemoteMachine(func=expensive_function, func_kwargs=dict(sim_dict=dict(a=2, b=3), workload_params=WorkloadParams()),  # this way, workload_params go directory to the function with **func_kwargs pickle.
#                       config=config)
#     m.run()
#     return m


# def try_run_on_remote():
#     run_on_remote()
#     run_on_remote()
#     i3 = run_on_remote()
#     i3.check_job_status()
#     i3.download_results(r=True)
#     i3.delete_remote_results()


# def run_on_cloud():
#     from machineconfig.cluster.remote_machine import RemoteMachine, RemoteMachineConfig, CloudManager
#     from machineconfig.cluster.templates.utils import expensive_function
#     from machineconfig.cluster.self_ssh import SelfSSH
#     config = RemoteMachineConfig(
#         # connection
#         ssh_obj=SelfSSH(),  # overrides ssh_params
#         description="Description of running an expensive function",  # job_id=, base_dir="",
#         # data
#         copy_repo=False, update_repo=True, install_repo=False, update_essential_repos=True, data=[], transfer_method="cloud", cloud_name="oduq1",
#         # remote machine behaviour
#         open_console=True, notify_upon_completion=True, to_email=None, email_config_name=None,
#         kill_on_completion=False,
#         launch_method="cloud_manager",
#         # execution behaviour
#         ipython=False, interactive=False, pdb=False, pudb=False, wrap_in_try_except=True,
#         workload_params=None,  # to be added later per sub-job.
#         # resources
#         lock_resources=True, max_simulataneous_jobs=2, parallelize=False, )
#     m = RemoteMachine(func=expensive_function, func_kwargs=dict(sim_dict=dict(a=2, b=3)), config=config)
#     res = m.submit_to_cloud(split=2, cm=CloudManager(max_jobs=1))
#     return res


# if __name__ == '__main__':
#     pass
