import psutil
import time
import sys
import platform
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.align import Align
from rich.live import Live
from rich import box

# Initialize Console
console = Console()

class SystemScanner:
    def __init__(self):
        self.specs = {}
        self.score = 0
        self.gflops = 0.0
        self.tier = ""

    def get_size(self, bytes, suffix="B"):
        """Scale bytes to its proper format"""
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor

    def scan_hardware(self):
        """Gather hardware specs using psutil"""
        
        # CPU Info
        # logical=False gives physical cores, True gives logical threads
        p_cores = psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True)
        l_cores = psutil.cpu_count(logical=True)
        
        # Frequency
        try:
            freq = psutil.cpu_freq()
            # Handle cases where max is 0.0 (common on some Linux/Apple Silicon)
            max_freq = freq.max if freq.max > 0 else freq.current
            current_freq = freq.current
        except Exception:
            max_freq = 2500 # Fallback assumption
            current_freq = 2500

        # Memory Info
        svmem = psutil.virtual_memory()
        
        self.specs = {
            "p_cores": p_cores,
            "l_cores": l_cores,
            "max_freq": max_freq,
            "current_freq": current_freq,
            "total_ram": svmem.total,
            "available_ram": svmem.available,
            "percent_ram": svmem.percent,
            "ctx_switches": 0, # Placeholder for live stats if needed
            "interrupts": 0
        }

    def calculate_metrics(self):
        """
        Calculates both the heuristic 'Compute Power Index' and the 
        Theoretical Maximum GFLOPS.
        """
        s = self.specs
        
        # --- 1. Compute Index (Synthetic Score) ---
        # Base Core Power: Physical cores weighted more than threads
        core_score = (s['p_cores'] * 100) + ((s['l_cores'] - s['p_cores']) * 30)
        
        # Frequency Multiplier (Normalized to 2.5GHz baseline)
        ghz = s['max_freq'] / 1000
        freq_multiplier = ghz / 2.5 
        
        cpu_total = core_score * freq_multiplier
        
        # Memory Bonus (5 points per GB)
        ram_gb = s['total_ram'] / (1024**3)
        ram_score = ram_gb * 5 
        
        self.score = int(cpu_total + ram_score)
        
        # --- 2. Theoretical GFLOPS (Rpeak) ---
        # Formula: Physical Cores * Frequency(GHz) * FLOPs/Cycle
        # Assumption: Modern CPU with AVX2 support (~16 DP FLOPs/cycle)
        # Note: This is a theoretical upper bound, not a benchmark result.
        ops_per_cycle = 16 
        self.gflops = s['p_cores'] * ghz * ops_per_cycle

        # Determine Tier
        if self.score < 500: self.tier = "[grey50]OBSOLETE[/grey50]"
        elif self.score < 1000: self.tier = "[green]CONSUMER[/green]"
        elif self.score < 2000: self.tier = "[blue]WORKSTATION[/blue]"
        elif self.score < 4000: self.tier = "[magenta]HIGH-PERFORMANCE[/magenta]"
        else: self.tier = "[bold red]SERVER GRADE / BEAST[/bold red]"

    def render_dashboard(self):
        """Generates the Rich renderables"""
        
        # 1. Header
        header = Panel(
            Align.center(
                Text("SYSTEM COMPUTE ANALYZER", style="bold white on blue", justify="center")
            ),
            box=box.HEAVY_EDGE,
            style="blue"
        )

        # 2. CPU Table
        cpu_table = Table(show_header=True, header_style="bold cyan", expand=True, box=box.SIMPLE)
        cpu_table.add_column("Attribute", style="dim")
        cpu_table.add_column("Value", style="bold white", justify="right")
        
        cpu_table.add_row("Physical Cores", str(self.specs['p_cores']))
        cpu_table.add_row("Logical Threads", str(self.specs['l_cores']))
        cpu_table.add_row("Max Frequency", f"{self.specs['max_freq']:.0f} MHz")
        cpu_table.add_row("Current Frequency", f"{self.specs['current_freq']:.0f} MHz")
        cpu_table.add_row("Architecture", platform.machine() or "Unknown")

        # 3. Memory Table
        mem_table = Table(show_header=True, header_style="bold magenta", expand=True, box=box.SIMPLE)
        mem_table.add_column("Attribute", style="dim")
        mem_table.add_column("Value", style="bold white", justify="right")
        
        mem_table.add_row("Total Memory", self.get_size(self.specs['total_ram']))
        mem_table.add_row("Available", self.get_size(self.specs['available_ram']))
        mem_table.add_row("Usage", f"{self.specs['percent_ram']}%")
        
        # 4. Score Panel
        score_text = Text()
        score_text.append("\nCOMPUTE INDEX: ", style="dim white")
        score_text.append(f"{self.score}", style="bold yellow")
        score_text.append("\nTHEORETICAL RPEAK: ", style="dim white")
        score_text.append(f"{self.gflops:.2f} GFLOPS", style="bold red underline")
        score_text.append(f"\n\nTIER: {self.tier}")
        
        score_panel = Panel(
            Align.center(score_text),
            box=box.DOUBLE,
            border_style="yellow",
            title="Performance Metrics",
            padding=(1, 2)
        )

        # Layout Composition
        layout = Layout()
        layout.split_column(
            Layout(header, size=3),
            Layout(name="body"),
            Layout(score_panel, size=9)
        )
        
        layout["body"].split_row(
            Layout(Panel(cpu_table, title="[cyan]CPU SCALAR[/cyan]", border_style="cyan")),
            Layout(Panel(mem_table, title="[magenta]MEMORY MATRIX[/magenta]", border_style="magenta"))
        )
        
        return layout

def main():
    scanner = SystemScanner()
    
    console.clear()
    
    # Phase 1: The "Scan" Effect
    with Progress(
        SpinnerColumn(style="bold cyan"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None, complete_style="blue", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        expand=True
    ) as progress:
        
        task1 = progress.add_task("[cyan]Probing CPU Architecture...", total=100)
        task2 = progress.add_task("[magenta]Analyzing Memory Banks...", total=100, start=False)
        task3 = progress.add_task("[yellow]Calculating Vector Potential...", total=100, start=False)

        # Simulate work
        while not progress.finished:
            # Task 1: CPU
            if not progress.finished:
                progress.update(task1, advance=2.5)
                if progress.tasks[0].completed >= 100:
                    progress.start_task(task2)
                    progress.update(task2, advance=3.5)
            
            # Task 2: RAM
            if progress.tasks[1].started:
                if progress.tasks[1].completed >= 100:
                    progress.start_task(task3)
                    progress.update(task3, advance=4.5)
            
            # Real work happens instantly, but we pace it for effect
            if progress.tasks[0].completed == 50:
                scanner.scan_hardware()
                
            time.sleep(0.03)

    # Phase 2: Calculation Logic
    scanner.calculate_metrics()
    
    # Phase 3: The Reveal
    console.print(scanner.render_dashboard())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]Analysis Aborted by User[/bold red]")