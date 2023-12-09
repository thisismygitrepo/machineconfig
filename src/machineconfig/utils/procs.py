
"""Procs
"""
import psutil
import pandas as pd
from tqdm import tqdm
from pytz import timezone
from machineconfig.utils.utils import display_options
from typing import Optional

pd.options.display.max_rows = 10000


def get_processes_accessing_file(path: str):
    res: dict[int, list[str]] = {}
    for proc in tqdm(psutil.process_iter()):
        try:
            files = proc.open_files()
        except psutil.AccessDenied:
            continue
        tmp = [file.path for file in files if path in file.path]
        if len(tmp) > 0:
            res[proc.pid] = tmp
    df = pd.DataFrame(res.items(), columns=['pid', 'files'])
    return df


def kill_process(name: str):
    for proc in psutil.process_iter():
        if proc.name() == name:
            proc.kill()


class ProcessManager:
    def __init__(self):
        process_info = []
        for proc in tqdm(psutil.process_iter(), desc="Reading Processes"):
            try:
                mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
                process_info.append([proc.pid, proc.name(), proc.username(), proc.cpu_percent(), mem_usage_mb, proc.status(), proc.create_time(), " ".join(proc.cmdline())])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
        df = pd.DataFrame(process_info)
        df.columns = pd.Index(['pid', 'name', 'username', 'cpu_percent', 'memory_usage_mb', 'status', 'create_time', 'command'])
        df['create_time'] = pd.to_datetime(df['create_time'], unit='s', utc=True).apply(lambda x: x.tz_convert(timezone('Australia/Adelaide')))
        df = df.sort_values(by='memory_usage_mb', ascending=False).reset_index(drop=True)
        self.df = df

    def choose_and_kill(self):
        options = str(self.df).split("\n")[1:]
        res = display_options(options=str(self.df).split("\n"), msg="", fzf=True, multi=True)
        indices = [options.index(val) for val in res]
        sub_df = self.df.iloc[indices]
        print(self.df)
        print(sub_df)
        from crocodile.core import Struct
        for idx, (_, row) in enumerate(sub_df.iterrows()):
            Struct(row.to_dict()).print(as_config=True, title=f"Process {idx}")
        kill_all = input("🔪 Confirm killing ALL? y/[n] ").lower() == "y"
        if kill_all:
            self.kill(pids=sub_df.pid.to_list())
            return
        kill_by_index = input("🔫 Kill by index? 1 4 ... /[n] ")
        if kill_by_index != "":
            indices = [int(val) for val in kill_by_index.split(" ")]
            sub_sub_df = sub_df.iloc[indices]
            for idx2, row in sub_sub_df.iterrows():
                Struct(row.to_dict()).print(as_config=True, title=f"Process {idx2}")
            _ = self.kill(pids=sub_sub_df.pid.to_list()) if input("Confirm kill? y/[n] ").lower() == "y" else None
        print("🫠🐔 Not killing any process.")

    def filter_and_kill(self, name: Optional[str] = None):
        _ = 20
        df_sub = self.df.query(f"name == '{name}' ").sort_values(by='create_time', ascending=True)
        self.kill(pids=df_sub.pid.to_list())

    def kill(self, names: Optional[list[str]] = None, pids: Optional[list[int]] = None, commands: Optional[list[str]] = None):
        if names is None and pids is None and commands is None:
            raise ValueError('names, pids and commands cannot all be None')
        if names is None: names = []
        if pids is None: pids = []
        if commands is None: commands = []
        for name in names:
            rows = self.df[self.df['name'] == name]
            if len(rows) > 0:
                for _idx, a_row in rows.iterrows():
                    psutil.Process(a_row.pid).kill()
                    print(f'💀 Killed process {name} with pid {a_row.pid}. It lived {get_age(a_row.create_time)}. RIP 🪦💐')
            else: print(f'No process named {name} found')
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.kill()
                print(f'💀 Killed process with pid {pid} and name {proc.name()}.  It lived {get_age(proc.create_time())}. RIP 🪦💐')
            except psutil.NoSuchProcess: print(f'No process with pid {pid} found')
        for command in commands:
            rows = self.df[self.df['command'].str.contains(command)]
            if len(rows) > 0:
                for _idx, a_row in rows.iterrows():
                    psutil.Process(a_row.pid).kill()
                    print(f'💀 Killed process with `{command}` in its command & pid = {a_row.pid}. It lived {get_age(a_row.create_time)}. RIP 🪦💐')
            else: print(f'No process has `{command}` in its command.')


def get_age(create_time: float):
    try: age = pd.Timestamp.now(tz="Australia/Adelaide") - pd.to_datetime(create_time, unit="s", utc=True).tz_convert(timezone("Australia/Adelaide"))
    except Exception as e:
        try: age = pd.Timestamp.now() - pd.to_datetime(create_time, unit="s", utc=True).tz_localize(tz=None)
        except Exception as ee:  # type: ignore
            return f"unknown due to {ee} and {e}"
    return age


if __name__ == '__main__':
    pass
