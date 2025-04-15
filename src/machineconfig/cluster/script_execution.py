"""
Job Execution Script
"""

import os
import getpass
import platform

from crocodile.core import Struct as S
from crocodile.file_management import P, Read
from crocodile.meta import generate_readme, Terminal
from machineconfig.cluster.loader_runner import WorkloadParams, JOB_STATUS
from machineconfig.cluster.remote_machine import RemoteMachineConfig
from machineconfig.cluster.file_manager import FileManager
from machineconfig.cluster.job_params import JobParams

from importlib.machinery import SourceFileLoader
from rich.console import Console
from rich.panel import Panel
from rich import inspect
from rich.text import Text
import pandas as pd

console = Console()

# EXTRA-PLACEHOLDER-PRE

_ = SourceFileLoader, WorkloadParams

params = JobParams.from_empty()

print("\n" + "═" * 80 + "\n")
manager: FileManager = FileManager.from_pickle(params.file_manager_path)
manager.secure_resources()
pid: int = os.getpid()
manager.execution_log_dir.expanduser().joinpath("pid.txt").create(parents_only=True).write_text(str(pid))
job_status: JOB_STATUS = "running"
manager.execution_log_dir.expanduser().joinpath("status.txt").write_text(job_status)


# keep those values after lock is released
time_at_execution_start_utc = pd.Timestamp.utcnow()
time_at_execution_start_local = pd.Timestamp.now()
manager.execution_log_dir.expanduser().create().joinpath("start_time.txt").write_text(str(time_at_execution_start_local))
func_kwargs = Read.pickle(path=manager.kwargs_path.expanduser())

# EXTRA-PLACEHOLDER-POST


# ######################### EXECUTION ####################################

print("\n" + "═" * 80 + "\n")
console.rule(title="🚀 PYTHON EXECUTION SCRIPT - STARTING 🚀", style="bold red", characters="═")
print("\n" + "═" * 80 + "\n")

console.print(f"""
📂 Executing File: {P(rf'{params.repo_path_rh}').expanduser().collapseuser().as_posix()}/{params.file_path_r}
🔧 Function: {params.func_name}
⏰ Time: {time_at_execution_start_local}
""", style="bold blue")

if isinstance(func_kwargs, dict): 
    S(func_kwargs).print(title="📋 Function Arguments", as_config=True)
else: 
    inspect(func_kwargs, value=False, title=f"📋 Function Arguments from `{manager.kwargs_path.collapseuser().as_posix()}`", docs=False, sort=False)

print("\n" + "•" * 60 + "\n")

res = ""
func = ""

# execution_line

print("\n" + "•" * 60 + "\n")
console.rule(title="✅ FINISHED PYTHON EXECUTION SCRIPT ✅", characters="═", style="bold green")
print("\n" + "═" * 80 + "\n")

# ######################### END OF EXECUTION #############################


if type(res) is P or (type(res) is str and P(res).expanduser().exists()):
    res_folder = P(res).expanduser()
else:
    res_folder = P.tmp(folder=rf"tmp_dirs/{manager.job_id}").create()
    console.print(Panel(f"""
⚠️  WARNING ⚠️
The executed function did not return a path to a results directory.
Execution metadata will be saved separately in:
{res_folder.collapseuser().as_posix()}
""", title="📁 Result Directory Warning", border_style="yellow"))
    print("\n\n")
    # try:
        # Save.pickle(obj=res, path=res_folder.joinpath("result.pkl"))
    # except TypeError as e:
        # print(e)
        # print(f"Could not pickle res object to path `{res_folder.joinpath('result.pkl').collapseuser().as_posix()}`.")

time_at_execution_end_utc = pd.Timestamp.utcnow()
time_at_execution_end_local = pd.Timestamp.now()
delta = time_at_execution_end_utc - time_at_execution_start_utc
exec_times = S({"start_utc 🌍⏲️": time_at_execution_start_utc, "end_utc 🌍⏰": time_at_execution_end_utc,
                   "start_local ⏲️": time_at_execution_start_local, "end_local ⏰": time_at_execution_end_local, "delta ⏳": delta,
                   "submission_time": manager.submission_time, "wait_time": time_at_execution_start_local - manager.submission_time})

# save the following in results folder and execution log folder.:
manager.execution_log_dir.expanduser().joinpath("end_time.txt").write_text(str(time_at_execution_end_local))
manager.execution_log_dir.expanduser().joinpath("results_folder_path.txt").write_text(res_folder.collapseuser().as_posix())
manager.execution_log_dir.expanduser().joinpath("error_message.txt").write_text(params.error_message)
exec_times.save(path=manager.execution_log_dir.expanduser().joinpath("execution_times.Struct.pkl"))
if params.error_message == "":
    job_status = "completed"
    manager.execution_log_dir.expanduser().joinpath("status.txt").write_text(job_status)
    print(f"""
✅ ═════════════════════ JOB COMPLETED SUCCESSFULLY ═════════════════════
🔖 Job ID: {manager.job_id}
⏱️  Total execution time: {delta}
📂 Results located at: {res_folder.collapseuser().as_posix()}
══════════════════════════════════════════════════════════════════════
""")
else:
    job_status = "failed"
    manager.execution_log_dir.expanduser().joinpath("status.txt").write_text(job_status)
    print(f"""
❌ ═════════════════════ JOB EXECUTION FAILED ═════════════════════
🔖 Job ID: {manager.job_id}
⏱️  Total execution time: {delta}
🔍 Error message: {params.error_message}
📂 Results located at: {res_folder.collapseuser().as_posix()}
═════════════════════════════════════════════════════════════════
""")


generate_readme(path=manager.job_root.expanduser().joinpath("execution_log.md"), obj=func, desc=f'''

Job executed via tb.cluster.Machine
remote: {params.ssh_repr}
job_id: {manager.job_id}

py_script_path @ `{manager.py_script_path.collapseuser()}`
shell_script_path @ `{manager.shell_script_path.collapseuser()}`
kwargs_path @ `{manager.kwargs_path.collapseuser()}`

### Execution Time:
{exec_times.print(as_config=True, return_str=True)}

### Job description
{params.description}

''')


# manager.root_dir.expanduser().copy(folder=res_folder, overwrite=True)

# print to execution console:
exec_times.print(title="⏱️ Execution Times", as_config=True)
print("\n" + "─" * 60 + "\n")
ssh_repr_remote = params.ssh_repr_remote or f"{getpass.getuser()}@{platform.node()}"  # os.getlogin() can throw an error in non-login shells.
console.print(Panel(Text(f'''
ftprx {ssh_repr_remote} {res_folder.collapseuser()} -r
''', style="bold blue on white"), title="📥 Pull results with this line:", border_style="bold red"))


if params.session_name != "":
    if platform.system() == "Linux":
        Terminal().run(f"""zellij --session {params.session_name} action new-tab --name results  """)
        # --layout ~/code/machineconfig/src/machineconfig/settings/zellij/layouts/d.kdl --cwd {res_folder.as_posix()}
        Terminal().run(f"""zellij --session {params.session_name} action write-chars "cd {res_folder.as_posix()};lf" """)
    elif platform.system() == "Windows":
        Terminal().run(f"""wt --window {params.session_name} new-tab --title results -startingDirectory {res_folder.as_posix()} lf """)


# NOTIFICATION-CODE-PLACEHOLDER


manager.unlock_resources()
rm_conf: RemoteMachineConfig = Read.pickle(path=manager.remote_machine_config_path.expanduser())


if rm_conf.kill_on_completion:
    # assert rm_conf.launch_method == "cloud_manager"
    if platform.system() == "Linux":
        from machineconfig.cluster.session_managers import Zellij  # type: ignore  # pylint: disable=C0412
        current_session = Zellij.get_current_zellij_session()
        # Zellij.close_tab(sess_name=params.session_name, tab_name=params.tab_name)
        print(f"""
🔄 ════════════════ SESSION MANAGEMENT ════════════════
🛑 Killing session `{params.session_name}` on `{params.ssh_repr}`
════════════════════════════════════════════════════════
""")
        Terminal().run(f"zellij --session {current_session} go-to-tab-name '{params.tab_name}'; sleep 2; zellij --session {current_session} action close-tab").print()  # i.e. current tab
    elif platform.system() == "Windows":
        print(f"""
🔄 ════════════════ SESSION MANAGEMENT ════════════════
🛑 Killing session `{params.session_name}` on `{params.ssh_repr}`
════════════════════════════════════════════════════════
""")
        from machineconfig.utils.procs import ProcessManager
        pm = ProcessManager()
        pm.kill(commands=[params.session_name])
    else: raise NotImplementedError(f"❌ kill_on_completion is not implemented for platform `{platform.system()}`")
else:
    print(f"""
🔄 ════════════════ SESSION MANAGEMENT ════════════════
✅ Keeping the tab `{params.tab_name}` on `{params.ssh_repr}`
════════════════════════════════════════════════════════
""")


console.rule(title="🏁 END OF PYTHON EXECUTION SCRIPT 🏁", style="bold green", characters="═")
