# """
# Cluster Template
# """


# from machineconfig.cluster.distribute import WorkloadParams
# from machineconfig.cluster.distribute import RemoteMachineConfig, LoadCriterion, Cluster, ThreadLoadCalculator
# from typing import Any, List


# class ExpensiveComputation:
#     @staticmethod
#     def _split_into_chunks(items: List[int], num_chunks: int) -> List[List[int]]:
#         """Split a list of integers into near-equal contiguous chunks.

#         Ensures no empty chunks are returned even if num_chunks > len(items).
#         """
#         if num_chunks <= 0:
#             return [items]
#         n = len(items)
#         if n == 0:
#             return []
#         base_size, remainder = divmod(n, num_chunks)
#         chunks: List[List[int]] = []
#         start_index = 0
#         for chunk_index in range(num_chunks):
#             current_size = base_size + (1 if chunk_index < remainder else 0)
#             if current_size == 0:
#                 # Skip empty chunk when num_chunks > n
#                 continue
#             end_index = start_index + current_size
#             chunks.append(items[start_index:end_index])
#             start_index = end_index
#         return chunks
#     @staticmethod
#     def func_single_job(workload_params: WorkloadParams, *args: Any, **kwargs: Any) -> P:
#         from machineconfig.cluster.templates.utils import expensive_function
#         res = expensive_function(workload_params=workload_params, *args, **kwargs)
#         return res

#     @staticmethod
#     def func(workload_params: WorkloadParams, **kwargs: Any) -> P:
#         # Build contiguous near-equal chunks across the index range
#         indices: List[int] = list(range(workload_params.idx_start, workload_params.idx_end, 1))
#         chunks: List[List[int]] = ExpensiveComputation._split_into_chunks(indices, workload_params.jobs)

#         # Create per-job workload params from chunks
#         per_job_workload_params: List[WorkloadParams] = [
#             WorkloadParams(
#                 idx_start=chunk[0],
#                 idx_end=chunk[-1] + 1,
#                 idx_max=workload_params.idx_max,
#                 jobs=workload_params.jobs,
#             )
#             for chunk in chunks
#             if len(chunk) > 0
#         ]

#         # Execute each job sequentially (replace former List.apply behavior)
#         # If parallel execution is needed, consider a ThreadPool/ProcessPool
#         results: List[PathExtended] = [
#             ExpensiveComputation.func_single_job(workload_params=job_params, **kwargs)
#             for job_params in per_job_workload_params
#         ]
#         return results[0]

#     @staticmethod
#     def submit():
#         config = RemoteMachineConfig(
#             # connection
#             ssh_params={}, description="Description of running an expensive function",  # job_id=, base_dir="",
#             # data
#             copy_repo=False, update_repo=False, install_repo=False, update_essential_repos=True, data=[],
#             transfer_method="sftp",
#             # remote machine behaviour
#             open_console=True, notify_upon_completion=True, to_email='random@email.com', email_config_name='enaut',
#             kill_on_completion=False,
#             # execution behaviour
#             ipython=True, interactive=True, pdb=False, pudb=False, wrap_in_try_except=True,
#             # resources
#             lock_resources=True, max_simulataneous_jobs=2, parallelize=True, )
#         ssh_params = [dict(host="thinkpad"), dict(host="p51s")]  # ,
#         # ssh_params = [dict(host="214676wsl"), dict(host="229234wsl")]
#         c = Cluster(func=ExpensiveComputation.func_single_job,
#                     func_kwargs=dict(sim_dict=dict(a=2, b=3)),
#                     ssh_params=ssh_params,
#                     remote_machine_config=config,
#                     thread_load_calc=ThreadLoadCalculator(num_jobs=3, load_criterion=LoadCriterion.cpu),  # if this machine can run 3 jobs at a time, how many can other machines do?
#                     )
#         c.run(run=True, machines_per_tab=len(ssh_params), window_number=354)
#         return c


# def try_run_on_cluster():
#     import time
#     ExpensiveComputation.submit()
#     ExpensiveComputation.submit()
#     cluster = ExpensiveComputation.submit()
#     # later ...
#     time.sleep(50)
#     c = Cluster.load(cluster.job_id)
#     c.open_mux(machines_per_tab=1)
#     c.check_job_status()
#     c.download_results()
#     # Delete remote results on all machines
#     for machine in c.machines:
#         machine.delete_remote_results()
#     return c


# if __name__ == '__main__':
#     pass
