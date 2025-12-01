# """Run cloud manager.
# """

# from machineconfig.cluster.cloud_manager import CloudManager
# from rich.console import Console  # Add import for Console
# from rich.panel import Panel  # Add import for Panel

# console = Console()

# BOX_WIDTH = 150  # width for box drawing


# def print_section_title(title: str):
#     """Prints a section title formatted nicely with a border and padding."""
#     console = Console()
#     console.print(Panel(title, title_align="left", expand=False))


# def main():
#     console = Console() # Add console initialization
#     console.print(Panel("☁️  Cloud Manager", title_align="left", expand=False))

#     parser.add_argument("-c", "--cloud", help="Rclone Config Name", action="store", type=str, default=None)
#     parser.add_argument("-s", "--serve", help="Start job server", action="store_true", default=False)
#     parser.add_argument("-R", "--reset_local", help="Clear local cache", action="store_true", default=False)
#     parser.add_argument("-r", "--rerun_jobs", help="Re-run jobs by bringing them back from wherever to the queue.", action="store_true", default=False)
#     parser.add_argument("-L", "--release_lock", help="Release lock.", action="store_true", default=False)
#     parser.add_argument("-f", "--queue_failed_jobs", help="Bring failed jobs back to queued jobs for a re-trial.", action="store_true", default=False)
#     parser.add_argument("-m", "--monitor_cloud", help="Monitor workers instead of running a job server.", action="store_true", default=False)
#     parser.add_argument("-j", "--num_jobs", help="Number of jobs the server will run in parallel.", action="store", type=int, default=1)
#     args = parser.parse_args()

#     init_line = f"🔧 Initializing Cloud Manager with {args.num_jobs} worker{'s' if args.num_jobs > 1 else ''}"
#     console.print(Panel(init_line, title_align="left", expand=False))

#     cm = CloudManager(max_jobs=args.num_jobs, cloud=args.cloud, reset_local=args.reset_local)

#     if args.release_lock:
#         line = "🔓 Releasing lock..."
#         console.print(Panel(line, title_align="left", expand=False))
#         cm.claim_lock()
#         cm.release_lock()
#         print("✅ Lock successfully released")

#     if args.queue_failed_jobs:
#         line = "🔄 Requeuing failed jobs..."
#         console.print(Panel(line, title_align="left", expand=False))
#         cm.clean_failed_jobs_mess()
#         print("✅ Failed jobs moved to queue")

#     if args.rerun_jobs:
#         line = "🔁 Rerunning jobs..."
#         console.print(Panel(line, title_align="left", expand=False))
#         cm.rerun_jobs()
#         print("✅ Jobs restarted successfully")

#     if args.monitor_cloud:
#         title = "👁️  STARTING CLOUD MONITOR"
#         console.print(Panel(title, title_align="left", expand=False))
#         cm.run_monitor()

#     if args.serve:
#         title1 = "🚀 STARTING JOB SERVER"
#         run_line = f"💻 Running {args.num_jobs} worker{'s' if args.num_jobs > 1 else ''}"
#         cloud_line = f"☁️  Cloud: {args.cloud if args.cloud else 'Default'}"
#         console.print(Panel(f"{title1}\n{run_line}\n{cloud_line}", title_align="left", expand=False))

#     title = "✅ Cloud Manager finished successfully"
#     console.print(Panel(title, title_align="left", expand=False))
#     import sys
#     sys.exit(0)


# if __name__ == '__main__':
#     main()
