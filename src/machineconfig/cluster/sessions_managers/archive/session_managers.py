
# """
# Session Manager
# """

# from machineconfig.cluster.self_ssh import SelfSSH

# from machineconfig.utils.io_save import save_yaml
# import time
# import subprocess
# from typing import Union


# class Zellij:
#     @staticmethod
#     def get_current_zellij_session() -> str:
#         try:
#                 output_lines = Terminal().run("zellij ls --no-formatting").op.split("\n")
#                 current_lines = [line for line in output_lines if "(current)" in line]
#                 return current_lines[0].split(" [Created")[0]
#         except IndexError as ie:
#             print("""Fails if there is no zellij session running, fails if there is no (current) suffix against the session name.""")
#             raise ie
#     @staticmethod
#     def get_new_session_command(sess_name: str) -> str: return f"zellij attach {sess_name} -c "  # -c means create if not exists.
#     @staticmethod
#     def get_new_session_ssh_command(ssh: Union[SSH, SelfSSH], sess_name: str):
#         if isinstance(ssh, SelfSSH): return Zellij.get_new_session_command(sess_name=sess_name)
#         return f"{ssh.get_ssh_conn_str()} -t {Zellij.get_new_session_command(sess_name=sess_name)}"
#     @staticmethod
#     def open_console(ssh: Union[SSH, SelfSSH], sess_name: str):
#         if isinstance(ssh, SelfSSH):
#             # return Terminal().run_async(Zellij.get_new_session_command(sess_name=sess_name), shell="powershell")
#             # currently, there is a limitation in zellij on creating a detached sessions, there is no way to fix this now.
#             # this will get stuck in the new session and won't run parallel.
#             return subprocess.Popen(["zellij", "--session", sess_name], shell=True, stdin=None, stdout=None, stderr=None)
#         return Terminal().run_async(Zellij.get_new_session_ssh_command(ssh=ssh, sess_name=sess_name))
#     @staticmethod
#     def asssert_session_started(ssh: Union[SSH, SelfSSH], sess_name: str):
#         while True:
#             raw_resp = ssh.run("zellij ls --no-formatting", verbose=False).op.split("\n")
#             current_sessions = [item.split(" [Created")[0] for item in raw_resp if "EXITED" not in item]
#             if sess_name in current_sessions:
#                 print(f"--> Session {sess_name} has started at the remote.")
#                 time.sleep(6)
#                 break
#             time.sleep(2)
#             print(f"--> Waiting for zellij session {sess_name} to start before sending fire commands ...")

#     @staticmethod
#     def close_tab(sess_name: str, tab_name: str):
#         cmd = f"""
# zellij --session {sess_name} action close-tab --tab-name '{tab_name}'
# zellij --session {sess_name} action new-tab --name '🖥️{tab_name}'
# zellij --session {sess_name} action new-tab --name '🔍{tab_name}'
# zellij --session {sess_name} action new-tab --name '🪪{tab_name}'
# zellij --session {sess_name} action new-tab --name '🧑‍💻{tab_name}'
# """
#         print(f"Closing tab `{tab_name}` in zellij session `{sess_name}` with command \n{cmd}")
#         return Terminal().run_script(cmd)

#     @staticmethod
#     def setup_layout(ssh: Union[SSH, SelfSSH], sess_name: str, cmd: str = "", run: bool = False, job_wd: str = "$HOME/tmp_results/remote_machines", tab_name: str = "", compact: bool = False):
#         sleep = 0.9
#         if run:
#             if cmd.startswith(". "): cmd = cmd[2:]
#             elif cmd.startswith("source "): cmd = cmd[7:]
#             else: pass
#             exe = f"""
# zellij --session {sess_name} action new-tab --name '{tab_name}'; sleep {sleep}
# zellij --session {sess_name} run -d down -- /bin/bash {cmd}; sleep {sleep}
# zellij --session {sess_name} action move-focus up; sleep {sleep}
# zellij --session {sess_name} action close-pane; sleep {sleep}
# """
#         else: exe = f"""
# zellij --session {sess_name} action write-chars "{cmd}"
# """
#         if not compact: cmd = f"""
# zellij --session {sess_name} action new-tab --name '{tab_name}'; sleep {sleep}
# zellij --session {sess_name} action rename-tab '🖥️{tab_name}'; sleep {sleep}  # rename the focused first tab
# zellij --session {sess_name} action new-tab --name '🔍{tab_name}'; sleep {sleep}
# zellij --session {sess_name} action write-chars htop; sleep {sleep}

# zellij --session {sess_name} action new-tab --name '📁{tab_name}'; sleep {sleep}
# zellij --session {sess_name} run --direction down --cwd {job_wd} -- lf; sleep {sleep}
# zellij --session {sess_name} action move-focus up; sleep {sleep}
# zellij --session {sess_name} action close-pane; sleep {sleep}

# zellij --session {sess_name} action new-tab --name '🪪{tab_name}'; sleep {sleep}
# zellij --session {sess_name} run --direction down -- neofetch;cpufetch; sleep {sleep}
# zellij --session {sess_name} action move-focus up; sleep {sleep}
# zellij --session {sess_name} action close-pane; sleep {sleep}

# zellij --session {sess_name} action new-tab --name '🧑‍💻{tab_name}'; sleep {sleep}
# zellij --session {sess_name} action write-chars "cd {job_wd}"; sleep {sleep}
# zellij --session {sess_name} action go-to-tab 1; sleep {sleep}
# {exe}

# """
#         else: cmd = exe
#         if isinstance(ssh, SelfSSH):
#             # print(1)
#             print(f"Setting up zellij layout `{sess_name}` on `{ssh.get_remote_repr()}` to run `{P(job_wd).name}`")
#             # return Terminal().run_script(cmd)  # Zellij not happy with launching scripts of zellij commands.
#             return Response.from_completed_process(subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True))
#         # print(2)
#         return ssh.run(cmd, desc=f"Setting up zellij layout on `{ssh.get_remote_repr()}`", verbose=False)
#     @staticmethod
#     def kill_session(ssh: Union[SSH, SelfSSH], sess_name: str):
#         cmd = f'zellij kill-session {sess_name}'
#         return ssh.run(cmd, desc=f"Killing zellij session `{sess_name}` on `{ssh.get_remote_repr()}`", verbose=False)


# class WindowsTerminal:
#     @staticmethod
#     def kill_session(sess_name: str):
#         from machineconfig.utils.procs import ProcessManager
#         pm = ProcessManager()
#         pm.kill(commands=[sess_name])
#     @staticmethod
#     def open_reference(): PathExtended(r"https://learn.microsoft.com/en-us/windows/terminal/command-line-arguments?tabs=windows")()
#     @staticmethod
#     def get_new_session_command(sess_name: str): return f"wt -w {sess_name} -d ."
#     @staticmethod
#     def get_new_session_ssh_command(ssh: Union[SSH, SelfSSH], sess_name: str):
#         if isinstance(ssh, SelfSSH): return WindowsTerminal.get_new_session_command(sess_name=sess_name)
#         return f"{ssh.get_ssh_conn_str()} -t {WindowsTerminal.get_new_session_command(sess_name=sess_name)}"
#     @staticmethod
#     def open_console(ssh: Union[SSH, SelfSSH], sess_name: str):
#         if isinstance(ssh, SelfSSH):
#             # return Terminal().run_async(WindowsTerminal.get_new_session_command(sess_name=sess_name), shell="powershell")
#             return subprocess.Popen(["wt", "--window", sess_name], shell=True, stdin=None, stdout=None, stderr=None)
#         return Terminal().run_async(WindowsTerminal.get_new_session_ssh_command(ssh=ssh, sess_name=sess_name), shell="pwsh")
#     @staticmethod
#     def asssert_session_started(ssh: Union[SSH, SelfSSH], sess_name: str):
#         _ = sess_name, ssh
#         time.sleep(6)
#         return True
#     @staticmethod
#     def setup_layout(ssh: Union[SSH, SelfSSH], sess_name: str, tab_name: str = "", cmd: str = "", run: bool = True, job_wd: str = "$HOME/tmp_results/remote_machines", compact: bool = True):
#         if run:
#             if cmd.startswith(". "): cmd = cmd[2:]
#             elif cmd.startswith("source "): cmd = cmd[7:]
#             else: pass
#             exe: str = f"""
# wt --window {sess_name} new-tab --title '{tab_name}' pwsh -noExit -Command {cmd}
# """
#         else: raise NotImplementedError("I don't know how to write-chars in Windows Terminal")  # exe = f""" wt --window {sess_name} action write-chars "{cmd}" """
#         sleep = 0.9
#         if compact: cmd = f"""
# wt --window {sess_name} new-tab --title '💻{tab_name}' htop `; split-pane --horizontal  --title '📁{tab_name}' --startingDirectory {job_wd} --profile pwsh lf `;  split-pane --vertical  --title '🪪{tab_name}' powershell -noExit "$HOME/scripts/neofetch.ps1" `; move-focus up `;  split-pane --vertical --startingDirectory {job_wd} --title '🧑‍💻{tab_name}' --profile pwsh
# """  # when pane-splitting, the tab title goes to the last pane declared.
#         else: cmd = f"""'
# wt --window {sess_name} new-tab --title '💻{tab_name}' htop; sleep {sleep}
# wt --window {sess_name} new-tab --title '📁{tab_name}' --startingDirectory {job_wd} lf; sleep {sleep}
# wt --window {sess_name} new-tab --title '🪪{tab_name}' powershell -noExit "$HOME/scripts/neofetch.ps1"; sleep {sleep}
# wt --window {sess_name} new-tab --title '🧑‍💻{tab_name}' --startingDirectory {job_wd} --profile pwsh; sleep {sleep}
# """
#         cmd = cmd + f"\nsleep {sleep};" + exe
#         # print(cmd)
#         if isinstance(ssh, SelfSSH):
#             print(f"Firing WindowsTerminal Session `{sess_name}` on `{ssh.get_remote_repr()}` to run `{P(job_wd).name}`")
#             return Terminal().run_script(cmd, shell="pwsh")
#         return ssh.run(cmd, desc=f"Setting up WindowsTerminal layout on `{ssh.get_remote_repr()}`", verbose=False)


# class Mprocs:
#     @staticmethod
#     def get_template():
#         import machineconfig
#         return PathExtended(machineconfig.__file__).parent.joinpath(r"settings/mprocs/windows/mprocs.yaml").readit()
#     # def get_new_session_name(self): return f"mprocs{self.id}"
#     @staticmethod
#     def get_ssh_command(): return ""
#     def open_console(self, cmd: str, shell: str = "powershell"):
#         _ = cmd, shell
#         return "wt -w 0 -d ."
#     def get_layout(self):
#         temp = self.get_template()
#         temp.procs['main']['shell']['windows'] = "croshell"
#         _template_file = save_yaml(obj=temp, path=PathExtended.tmpfile(suffix=".yaml"))
#     def asssert_session_started(self):
#         time.sleep(3)
#         return True
