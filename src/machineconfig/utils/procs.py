
import psutil
import pandas as pd
from pytz import timezone


class ProcessManager:
    def __init__(self):
        process_info = []
        for proc in psutil.process_iter():
            try:
                mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
                process_info.append([proc.pid, proc.name(), proc.username(), proc.cpu_percent(), mem_usage_mb, proc.status(), proc.create_time()])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
        df = pd.DataFrame(process_info)
        df.columns = ['pid', 'name', 'username', 'cpu_percent', 'memory_usage_mb', 'status', 'create_time']
        df['create_time'] = pd.to_datetime(df['create_time'], unit='s', utc=True).apply(lambda x: x.tz_convert(timezone('Australia/Adelaide')))
        df = df.sort_values(by='memory_usage_mb', ascending=False).reset_index(drop=True)
        self.df = df

    def filter_and_kill(self, name):
        tmp = self.df.query(f"name == '{name}' ").sort_values(by='create_time', ascending=True)
        self.kill(pids=tmp.pid)

    def kill(self, names: list or None = None, pids: list or None = None):
        if names is None and pids is None:
            raise ValueError('names and pids cannot both be None')
        if names is None: names = []
        if pids is None: pids = []
        for name in names:
            rows = self.df[self.df['name'] == name]
            if len(rows) > 0:
                for pid in rows['pid'].values:
                    psutil.Process(pid).kill()
                    print(f'Killed process {name} with pid {pid}. It lived {pd.Timestamp.now() - pd.to_datetime(rows["create_time"].values[0], unit="s", utc=True).tz_convert(timezone("Australia/Adelaide"))}.')
            else:
                print(f'No process named {name} found')
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.kill()
                print(f'Killed process with pid {pid} and name {proc.name()}.  It lived {pd.Timestamp.now() - pd.to_datetime(proc.create_time(), unit="s", utc=True).tz_convert(timezone("Australia/Adelaide"))}.')
            except psutil.NoSuchProcess:
                print(f'No process with pid {pid} found')


if __name__ == '__main__':
    pass