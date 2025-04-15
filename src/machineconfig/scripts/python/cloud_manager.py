"""Run cloud manager.
"""

from machineconfig.cluster.loader_runner import CloudManager
import argparse


def main():
    print(f"""
╔{'═' * 70}╗
║ ☁️  Cloud Manager                                                         ║
╚{'═' * 70}╝
""")
    
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

    print(f"""
╭{'─' * 70}╮
│ 🔧 Initializing Cloud Manager with {args.num_jobs} worker{'s' if args.num_jobs > 1 else ''}    │
╰{'─' * 70}╯
""")
    
    cm = CloudManager(max_jobs=args.num_jobs, cloud=args.cloud, reset_local=args.reset_local)
    
    if args.release_lock:
        print(f"""
╭{'─' * 70}╮
│ 🔓 Releasing lock...                                                      │
╰{'─' * 70}╯
""")
        cm.claim_lock()
        cm.release_lock()
        print("✅ Lock successfully released")
        
    if args.queue_failed_jobs:
        print(f"""
╭{'─' * 70}╮
│ 🔄 Requeuing failed jobs...                                               │
╰{'─' * 70}╯
""")
        cm.clean_failed_jobs_mess()
        print("✅ Failed jobs moved to queue")
        
    if args.rerun_jobs:
        print(f"""
╭{'─' * 70}╮
│ 🔁 Rerunning jobs...                                                      │
╰{'─' * 70}╯
""")
        cm.rerun_jobs()
        print("✅ Jobs restarted successfully")
        
    if args.monitor_cloud:
        print(f"""
╔{'═' * 70}╗
║ 👁️  STARTING CLOUD MONITOR                                                 ║
╚{'═' * 70}╝
""")
        cm.run_monitor()
        
    if args.serve:
        print(f"""
╔{'═' * 70}╗
║ 🚀 STARTING JOB SERVER                                                    ║
╠{'═' * 70}╣
║ 💻 Running {args.num_jobs} worker{'s' if args.num_jobs > 1 else ''}                                                   ║
║ ☁️  Cloud: {args.cloud if args.cloud else 'Default'}                                               
╚{'═' * 70}╝
""")
        cm.serve()
        
    print(f"""
╔{'═' * 70}╗
║ ✅ Cloud Manager finished successfully                                    ║
╚{'═' * 70}╝
""")
    import sys
    sys.exit(0)


if __name__ == '__main__':
    main()
