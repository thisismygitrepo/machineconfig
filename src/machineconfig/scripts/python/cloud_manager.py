
"""Run cloud manager.
"""

from crocodile.cluster.loader_runner import CloudManager
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cloud", help="Rclone Config Name", action="store", type=str, default=None)
    parser.add_argument("-s", "--serve", help="Start job server", action="store_true", default=False)
    parser.add_argument("-R", "--reset_local", help="Clear local cache", action="store_true", default=False)
    parser.add_argument("-r", "--rerun_jobs", help="Re-run jobs by bringing them back from wherever to the queue.", action="store_true", default=False)
    parser.add_argument("-L", "--release_lock", help="Release lock.", action="store_true", default=False)
    parser.add_argument("-f", "--queue_failed_jobs", help="Bring failed jobs back to queued jobs for a re-trial.", action="store_true", default=False)
    parser.add_argument("-m", "--monitor_cloud", help="Monitor workers instead of running a job server.", action="store_true", default=False)
    parser.add_argument("-j", "--num_jobs", help="Number of jobs the server will run in parallel.", action="store", type=int, default=1)
    args = parser.parse_args()

    cm = CloudManager(max_jobs=args.num_jobs, cloud=args.cloud, reset_local=args.reset_local)
    if args.release_lock:
        cm.claim_lock()
        cm.release_lock()
    if args.queue_failed_jobs:
        cm.clean_failed_jobs_mess()
    if args.rerun_jobs:
        cm.rerun_jobs()
    if args.monitor_cloud:
        cm.run_monitor()
    if args.serve:
        cm.serve()
    import sys
    sys.exit(0)


if __name__ == '__main__':
    main()
