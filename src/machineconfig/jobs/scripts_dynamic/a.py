"""
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "rich",
#   "psutil",
# ]
# ///

"""


import platform
import time
from dataclasses import dataclass, field

import psutil
from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text


# ══════════════════════════════════════════════════════════════════════════════
# Constants & Configuration
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_FREQ_MHZ: float = 2500.0
OPS_PER_CYCLE_AVX2: int = 16  # AVX2: ~16 double-precision FLOPs/cycle
BYTES_PER_GB: int = 1024**3

# Tier thresholds and styling
TIER_CONFIG: list[tuple[int, str, str]] = [
    (500, "OBSOLETE", "grey50"),
    (1000, "CONSUMER", "green"),
    (2000, "WORKSTATION", "blue"),
    (4000, "HIGH-PERFORMANCE", "magenta"),
    (999999, "SERVER GRADE", "bold red"),
]

# Visual theme
THEME = {
    "primary": "cyan",
    "secondary": "magenta",
    "accent": "yellow",
    "success": "green",
    "header_bg": "blue",
}

console = Console()


# ══════════════════════════════════════════════════════════════════════════════
# Data Structures
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class HardwareSpecs:
    """Container for hardware specifications."""

    physical_cores: int = 0
    logical_cores: int = 0
    max_freq_mhz: float = 0.0
    current_freq_mhz: float = 0.0
    total_ram_bytes: int = 0
    available_ram_bytes: int = 0
    ram_percent_used: float = 0.0
    architecture: str = ""
    cpu_model: str = ""


@dataclass
class ComputeMetrics:
    """Calculated compute performance metrics."""

    compute_index: int = 0
    theoretical_gflops: float = 0.0
    tier_name: str = ""
    tier_style: str = ""
    core_score: float = 0.0
    freq_multiplier: float = 0.0
    ram_score: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# System Scanner
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class SystemScanner:
    """Scans and analyzes system hardware for compute capability metrics."""

    specs: HardwareSpecs = field(default_factory=HardwareSpecs)
    metrics: ComputeMetrics = field(default_factory=ComputeMetrics)

    @staticmethod
    def format_bytes(num_bytes: int | float, suffix: str = "B") -> str:
        """Scale bytes to human-readable format with proper unit prefix."""
        factor = 1024.0
        value = float(num_bytes)
        for unit in ("", "K", "M", "G", "T", "P", "E"):
            if abs(value) < factor:
                return f"{value:.2f} {unit}{suffix}"
            value /= factor
        return f"{value:.2f} Z{suffix}"

    def scan_hardware(self) -> None:
        """Gather hardware specs using psutil."""
        # CPU cores - prefer physical, fallback to logical
        physical = psutil.cpu_count(logical=False)
        logical = psutil.cpu_count(logical=True)
        p_cores = physical if physical else (logical if logical else 1)
        l_cores = logical if logical else p_cores

        # CPU frequency with fallback
        max_freq = DEFAULT_FREQ_MHZ
        current_freq = DEFAULT_FREQ_MHZ
        try:
            freq = psutil.cpu_freq()
            if freq:  # Can be None on some systems
                max_freq = freq.max if freq.max > 0 else freq.current
                current_freq = freq.current
        except (AttributeError, FileNotFoundError, PermissionError, RuntimeError):
            pass  # Use defaults

        # Memory info
        vmem = psutil.virtual_memory()

        # CPU model detection
        cpu_model = self._detect_cpu_model()

        self.specs = HardwareSpecs(
            physical_cores=p_cores,
            logical_cores=l_cores,
            max_freq_mhz=max_freq,
            current_freq_mhz=current_freq,
            total_ram_bytes=vmem.total,
            available_ram_bytes=vmem.available,
            ram_percent_used=vmem.percent,
            architecture=platform.machine() or "Unknown",
            cpu_model=cpu_model,
        )

    @staticmethod
    def _detect_cpu_model() -> str:
        """Detect CPU model string from platform info."""
        try:
            return platform.processor() or "Unknown Processor"
        except (OSError, AttributeError):
            return "Unknown Processor"

    def calculate_metrics(self) -> None:
        """Calculate compute power index and theoretical GFLOPS."""
        s = self.specs

        # Core score: physical cores weighted heavily, threads add bonus
        thread_bonus = max(0, s.logical_cores - s.physical_cores)
        core_score = (s.physical_cores * 100.0) + (thread_bonus * 30.0)

        # Frequency multiplier (normalized to 2.5 GHz baseline)
        ghz = s.max_freq_mhz / 1000.0
        freq_multiplier = ghz / 2.5

        cpu_total = core_score * freq_multiplier

        # Memory bonus (5 points per GB)
        ram_gb = s.total_ram_bytes / BYTES_PER_GB
        ram_score = ram_gb * 5.0

        compute_index = int(cpu_total + ram_score)

        # Theoretical GFLOPS (Rpeak) = cores × GHz × FLOPs/cycle
        theoretical_gflops = s.physical_cores * ghz * OPS_PER_CYCLE_AVX2

        # Determine tier
        tier_name, tier_style = "UNKNOWN", "white"
        for threshold, name, style in TIER_CONFIG:
            if compute_index < threshold:
                tier_name, tier_style = name, style
                break

        self.metrics = ComputeMetrics(
            compute_index=compute_index,
            theoretical_gflops=theoretical_gflops,
            tier_name=tier_name,
            tier_style=tier_style,
            core_score=core_score,
            freq_multiplier=freq_multiplier,
            ram_score=ram_score,
        )

    def _build_header(self) -> Panel:
        """Build the header panel."""
        title = Text()
        title.append("╔══════════════════════════════════════╗\n", style="bold cyan")
        title.append("║  ", style="bold cyan")
        title.append("SYSTEM COMPUTE ANALYZER", style="bold white")
        title.append("  ║\n", style="bold cyan")
        title.append("╚══════════════════════════════════════╝", style="bold cyan")

        return Panel(
            Align.center(title),
            box=box.DOUBLE,
            style=THEME["header_bg"],
            padding=(0, 2),
        )

    def _build_cpu_panel(self) -> Panel:
        """Build the CPU information panel."""
        s = self.specs
        table = Table(
            show_header=True,
            header_style=f"bold {THEME['primary']}",
            expand=True,
            box=box.ROUNDED,
            border_style="dim cyan",
            row_styles=["", "dim"],
        )
        table.add_column("⚡ Attribute", style="cyan", no_wrap=True)
        table.add_column("Value", style="bold white", justify="right")

        # Cores with visual indicator
        cores_bar = "█" * min(s.physical_cores, 16) + "░" * max(0, 16 - s.physical_cores)
        table.add_row("Physical Cores", f"{s.physical_cores}  [{THEME['primary']}]{cores_bar}[/]")
        table.add_row("Logical Threads", str(s.logical_cores))
        table.add_row("──────────────", "────────────")
        table.add_row("Max Frequency", f"[bold yellow]{s.max_freq_mhz:,.0f}[/] MHz")
        table.add_row("Current Freq", f"{s.current_freq_mhz:,.0f} MHz")
        table.add_row("Architecture", f"[bold]{s.architecture}[/]")

        return Panel(
            table,
            title=f"[bold {THEME['primary']}]◆ CPU COMPUTE UNIT ◆[/]",
            border_style=THEME["primary"],
            box=box.HEAVY,
            padding=(1, 1),
        )

    def _build_memory_panel(self) -> Panel:
        """Build the memory information panel."""
        s = self.specs
        table = Table(
            show_header=True,
            header_style=f"bold {THEME['secondary']}",
            expand=True,
            box=box.ROUNDED,
            border_style="dim magenta",
            row_styles=["", "dim"],
        )
        table.add_column("💾 Attribute", style="magenta", no_wrap=True)
        table.add_column("Value", style="bold white", justify="right")

        # Memory usage bar
        used_blocks = int(s.ram_percent_used / 10)
        free_blocks = 10 - used_blocks
        mem_bar = f"[green]{'█' * free_blocks}[/][red]{'█' * used_blocks}[/]"

        table.add_row("Total Memory", f"[bold yellow]{self.format_bytes(s.total_ram_bytes)}[/]")
        table.add_row("Available", self.format_bytes(s.available_ram_bytes))
        table.add_row("──────────────", "────────────")
        table.add_row("Usage", f"{s.ram_percent_used:.1f}%  {mem_bar}")

        return Panel(
            table,
            title=f"[bold {THEME['secondary']}]◆ MEMORY MATRIX ◆[/]",
            border_style=THEME["secondary"],
            box=box.HEAVY,
            padding=(1, 1),
        )

    def _build_metrics_panel(self) -> Panel:
        """Build the performance metrics panel."""
        m = self.metrics

        # Build score display with visual flair
        content = Table.grid(padding=(0, 2), expand=True)
        content.add_column(justify="center")

        # Main score with large emphasis
        score_text = Text()
        score_text.append("\n┌─────────────────────────────────────────┐\n", style="dim yellow")
        score_text.append("│  COMPUTE POWER INDEX  │  ", style="dim yellow")
        score_text.append(f"{m.compute_index:,}", style="bold yellow on black")
        score_text.append("  │\n", style="dim yellow")
        score_text.append("└─────────────────────────────────────────┘\n", style="dim yellow")

        content.add_row(Align.center(score_text))

        # Breakdown table
        breakdown = Table(show_header=False, box=None, padding=(0, 4))
        breakdown.add_column(style="dim")
        breakdown.add_column(style="bold", justify="right")
        breakdown.add_row("Core Score:", f"{m.core_score:.0f}")
        breakdown.add_row("Freq Multiplier:", f"×{m.freq_multiplier:.2f}")
        breakdown.add_row("RAM Bonus:", f"+{m.ram_score:.0f}")

        content.add_row(Align.center(breakdown))

        # Theoretical GFLOPS
        gflops_text = Text()
        gflops_text.append("\n⚡ Theoretical Rpeak: ", style="dim white")
        gflops_text.append(f"{m.theoretical_gflops:.2f} GFLOPS", style="bold red underline")
        gflops_text.append(" (AVX2)", style="dim")
        content.add_row(Align.center(gflops_text))

        # Tier with styled badge
        tier_text = Text()
        tier_text.append("\n\n◉ CLASSIFICATION: ", style="bold white")
        tier_text.append(f" {m.tier_name} ", style=f"bold white on {m.tier_style}")
        tier_text.append("\n", style="")
        content.add_row(Align.center(tier_text))

        return Panel(
            content,
            title=f"[bold {THEME['accent']}]★ PERFORMANCE METRICS ★[/]",
            border_style=THEME["accent"],
            box=box.DOUBLE,
            padding=(1, 2),
        )

    def render_dashboard(self) -> Layout:
        """Generate the complete dashboard layout."""
        layout = Layout()

        layout.split_column(
            Layout(self._build_header(), name="header", size=5),
            Layout(name="body", ratio=2),
            Layout(Rule("─", style="dim"), name="divider", size=1),
            Layout(self._build_metrics_panel(), name="metrics", size=14),
        )

        layout["body"].split_row(
            Layout(self._build_cpu_panel(), name="cpu"),
            Layout(self._build_memory_panel(), name="memory"),
        )

        return layout


# ══════════════════════════════════════════════════════════════════════════════
# Progress Animation
# ══════════════════════════════════════════════════════════════════════════════


def run_scan_animation(scanner: SystemScanner) -> None:
    """Run the scanning progress animation."""
    scan_complete = False

    with Progress(
        SpinnerColumn("dots12", style="bold cyan"),
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
        TextColumn("[bold cyan]{task.percentage:>3.0f}%"),
        console=console,
        expand=True,
    ) as progress:
        task1 = progress.add_task(f"[{THEME['primary']}]⚙ Probing CPU Architecture...", total=100)
        task2 = progress.add_task(
            f"[{THEME['secondary']}]💾 Analyzing Memory Banks...",
            total=100,
            start=False,
        )
        task3 = progress.add_task(
            f"[{THEME['accent']}]📊 Calculating Vector Potential...",
            total=100,
            start=False,
        )

        while not progress.finished:
            # Task 1: CPU probe
            if progress.tasks[0].completed < 100:
                progress.update(task1, advance=2.5)
                if progress.tasks[0].completed >= 50 and not scan_complete:
                    scanner.scan_hardware()
                    scan_complete = True
            elif not progress.tasks[1].started:
                progress.start_task(task2)

            # Task 2: Memory analysis
            if progress.tasks[1].started and progress.tasks[1].completed < 100:
                progress.update(task2, advance=3.5)
            elif progress.tasks[1].completed >= 100 and not progress.tasks[2].started:
                progress.start_task(task3)

            # Task 3: Calculation
            if progress.tasks[2].started:
                progress.update(task3, advance=4.5)

            time.sleep(0.025)


# ══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    """Main entry point for the system compute analyzer."""
    scanner = SystemScanner()

    console.clear()
    console.print()

    # Phase 1: Animated scanning
    run_scan_animation(scanner)

    # Phase 2: Calculate metrics
    scanner.calculate_metrics()

    # Phase 3: Display results
    console.print()
    console.print(scanner.render_dashboard())
    console.print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]✖ Analysis Aborted by User[/bold red]\n")