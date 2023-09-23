
"""Run cloud manager.
"""

from crocodile.cluster.loader_runner import CloudManager
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cloud", help="Rclone Config Name", action="store", type=str, default=None)
    parser.add_argument("-r", "--reset_local", help="Clear local cache", action="store_true", default=False)
    parser.add_argument("-m", "--monitor_cloud", help="Monitor workers instead of running a job server.", action="store_true", default=False)
    args = parser.parse_args()

    cm = CloudManager(max_jobs=1, cloud=args.cloud, reset_local=args.reset_local)
    if args.monitor_cloud:
        cm.run_monitor()
    else:
        cm.run()


if __name__ == '__main__':
    main()
