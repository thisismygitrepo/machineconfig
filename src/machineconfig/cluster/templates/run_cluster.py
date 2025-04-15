
"""
Cluster Template
"""

from crocodile.core import List as L
from crocodile.file_management import P
from machineconfig.cluster.distribute import WorkloadParams
from machineconfig.cluster.distribute import RemoteMachineConfig, LoadCriterion, Cluster, ThreadLoadCalculator
from typing import Any


class ExpensiveComputation:
    @staticmethod
    def func_single_job(workload_params: WorkloadParams, *args: Any, **kwargs: Any) -> P:
        from machineconfig.cluster.templates.utils import expensive_function
        res = expensive_function(workload_params=workload_params, *args, **kwargs)
        return res

    @staticmethod
    def func(workload_params: WorkloadParams, **kwargs: Any) -> P:
        per_job_workload_params = L(range(workload_params.idx_start, workload_params.idx_end, 1)).split(to=workload_params.jobs).apply(lambda sub_list: WorkloadParams(idx_start=sub_list.list[0], idx_end=sub_list.list[-1] + 1, idx_max=workload_params.idx_max, jobs=workload_params.jobs))
        res: list[P] = L(per_job_workload_params).apply(lambda a_workload_params: ExpensiveComputation.func_single_job(workload_params=a_workload_params, **kwargs), jobs=workload_params.jobs).list
        return res[0]

    @staticmethod
    def submit():
        config = RemoteMachineConfig(
            # connection
            ssh_params={}, description="Description of running an expensive function",  # job_id=, base_dir="",
            # data
            copy_repo=False, update_repo=False, install_repo=False, update_essential_repos=True, data=[],
            transfer_method="sftp",
            # remote machine behaviour
            open_console=True, notify_upon_completion=True, to_email='random@email.com', email_config_name='enaut',
            kill_on_completion=False,
            # execution behaviour
            ipython=True, interactive=True, pdb=False, pudb=False, wrap_in_try_except=True,
            # resources
            lock_resources=True, max_simulataneous_jobs=2, parallelize=True, )
        ssh_params = [dict(host="thinkpad"), dict(host="p51s")]  # ,
        # ssh_params = [dict(host="214676wsl"), dict(host="229234wsl")]
        c = Cluster(func=ExpensiveComputation.func_single_job,
                    func_kwargs=dict(sim_dict=dict(a=2, b=3)),
                    ssh_params=ssh_params,
                    remote_machine_config=config,
                    thread_load_calc=ThreadLoadCalculator(num_jobs=3, load_criterion=LoadCriterion.cpu),  # if this machine can run 3 jobs at a time, how many can other machines do?
                    )
        c.run(run=True, machines_per_tab=len(ssh_params), window_number=354)
        return c


def try_run_on_cluster():
    import time
    ExpensiveComputation.submit()
    ExpensiveComputation.submit()
    cluster = ExpensiveComputation.submit()
    # later ...
    time.sleep(50)
    c = Cluster.load(cluster.job_id)
    c.open_mux(machines_per_tab=1)
    c.check_job_status()
    c.download_results()
    L(c.machines).delete_remote_results()
    return c


if __name__ == '__main__':
    pass
