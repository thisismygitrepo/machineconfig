
import psutil
import pandas as pd
from pytz import timezone
from machineconfig.utils.utils import display_options


pd.options.display.max_rows = 10000


class ProcessManager:
    def __init__(self):
        process_info = []
        for proc in psutil.process_iter():
            try:
                mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
                process_info.append([proc.pid, proc.name(), proc.username(), proc.cpu_percent(), mem_usage_mb, proc.status(), proc.create_time(), " ".join(proc.cmdline())])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
        df = pd.DataFrame(process_info)
        df.columns = ['pid', 'name', 'username', 'cpu_percent', 'memory_usage_mb', 'status', 'create_time', 'command']
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
        self.kill(pids=sub_df.pid) if input("Confirm kill? y/[n] ").lower() == "y" else print("Not killing")

    def filter_and_kill(self, name=None):
        _ = 20
        df_sub = self.df.query(f"name == '{name}' ").sort_values(by='create_time', ascending=True)
        self.kill(pids=df_sub.pid)

    def kill(self, names: list or None = None, pids: list or None = None, commands: list or None = None):
        if names is None and pids is None:
            raise ValueError('names and pids cannot both be None')
        if names is None: names = []
        if pids is None: pids = []
        if commands is None: commands = []
        for name in names:
            rows = self.df[self.df['name'] == name]
            if len(rows) > 0:
                for pid in rows['pid'].values:
                    psutil.Process(pid).kill()
                    age = pd.Timestamp.now(tz="Australia/Adeliade") - pd.to_datetime(rows["create_time"].values[0], unit="s", utc=True).tz_convert(timezone("Australia/Adelaide"))
                    print(f'Killed process {name} with pid {pid}. It lived {age}.')
            else:
                print(f'No process named {name} found')
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.kill()
                age = pd.Timestamp.now(tz="Australia/Adelaide") - pd.to_datetime(proc.create_time(), unit="s", utc=True).tz_convert(timezone("Australia/Adelaide"))
                print(f'Killed process with pid {pid} and name {proc.name()}.  It lived {age}.')
            except psutil.NoSuchProcess:
                print(f'No process with pid {pid} found')
        for command in commands:
            rows = self.df[self.df['command'].str.contains(command)]
            if len(rows) > 0:
                for pid in rows['pid'].values:
                    psutil.Process(pid).kill()
                    age = pd.Timestamp.now(tz="Australia/Adeliade") - pd.to_datetime(rows["create_time"].values[0], unit="s", utc=True).tz_convert(timezone("Australia/Adelaide"))
                    print(f'Killed process with `{command}` in its command & pid = {pid}. It lived {age}.')
            else:
                print(f'No process has `{command}` in its command.')


if __name__ == '__main__':
    pass
