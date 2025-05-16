"""Run cloud manager.
"""

from machineconfig.cluster.loader_runner import CloudManager
import argparse
from rich.console import Console
from rich.panel import Panel
from rich import box # Import box

console = Console()

BOX_WIDTH = 150  # width for box drawing


def _get_padding(text: str, padding_before: int = 2, padding_after: int = 1) -> str:
    """Calculate the padding needed to align the box correctly.
    
    Args:
        text: The text to pad
        padding_before: The space taken before the text (usually "║ ")
        padding_after: The space needed after the text (usually " ║")
    
    Returns:
        A string of spaces for padding
    """
    # Count visible characters (might not be perfect for all Unicode characters)
    text_length = len(text)
    padding_length = BOX_WIDTH - padding_before - text_length - padding_after
    return ' ' * max(0, padding_length)

def display_section_title(title):
    console.print(Panel(title, box=box.DOUBLE_EDGE, title_align="left")) # Replace print with Panel

def display_info(info_text):
    console.print(Panel(info_text, box=box.ROUNDED, title_align="left")) # Replace print with Panel

def display_warning(warning_text):
    console.print(Panel(warning_text, box=box.ROUNDED, border_style="yellow", title_align="left")) # Replace print with Panel

def display_error(error_text):
    console.print(Panel(error_text, box=box.ROUNDED, border_style="red", title_align="left")) # Replace print with Panel

def display_success(success_text):
    console.print(Panel(success_text, box=box.ROUNDED, border_style="green", title_align="left")) # Replace print with Panel


def main():
    display_section_title("☁️  Cloud Manager")
    
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

    init_line = f"🔧 Initializing Cloud Manager with {args.num_jobs} worker{'s' if args.num_jobs > 1 else ''}"
    display_info(init_line)
    
    cm = CloudManager(max_jobs=args.num_jobs, cloud=args.cloud, reset_local=args.reset_local)
    
    if args.release_lock:
        line = "🔓 Releasing lock..."
        display_info(line)
        cm.claim_lock()
        cm.release_lock()
        display_success("✅ Lock successfully released")
        
    if args.queue_failed_jobs:
        line = "🔄 Requeuing failed jobs..."
        display_info(line)
        cm.clean_failed_jobs_mess()
        display_success("✅ Failed jobs moved to queue")
        
    if args.rerun_jobs:
        line = "🔁 Rerunning jobs..."
        display_info(line)
        cm.rerun_jobs()
        display_success("✅ Jobs restarted successfully")
        
    if args.monitor_cloud:
        title = "👁️  STARTING CLOUD MONITOR"
        display_section_title(title)
        cm.run_monitor()
        
    if args.serve:
        title1 = "🚀 STARTING JOB SERVER"
        run_line = f"💻 Running {args.num_jobs} worker{'s' if args.num_jobs > 1 else ''}"
        cloud_line = f"☁️  Cloud: {args.cloud if args.cloud else 'Default'}"
        display_section_title(title1)
        display_info(run_line)
        display_info(cloud_line)
        
    title = "✅ Cloud Manager finished successfully"
    display_section_title(title)
    import sys
    sys.exit(0)


if __name__ == '__main__':
    main()
