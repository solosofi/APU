import argparse
import time
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.progress_bar import ProgressBar as Bar
from rich.text import Text

from cpuoptmonitor.profiler import RealTimeProfiler

console = Console()

def generate_layout(data: dict) -> Layout:
    """Generates the layout for the dashboard."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main"),
    )
    header_text = Text("CPU Adaptive Monitor", justify="center", style="bold magenta")
    layout["header"].update(header_text)
    layout["main"].split_row(Layout(name="left"), Layout(name="right", ratio=2))

    # Left panel with metrics
    metrics_table = Table.grid(expand=True)
    metrics_table.add_column(style="cyan")
    metrics_table.add_column(justify="right", style="green")

    total_usage = data.get('total_usage', 0.0)
    metrics_table.add_row("Total CPU Usage:", f"{total_usage:.1f}%")

    # Placeholder for future metrics
    metrics_table.add_row("Task:", "[yellow]N/A[/yellow]")
    metrics_table.add_row("Power:", "[yellow]N/A[/yellow]")
    metrics_table.add_row("Efficiency:", "[yellow]N/A[/yellow]")

    layout["left"].update(Panel(metrics_table, title="Live Metrics", border_style="blue"))

    # Right panel with optimizations and per-core usage
    right_layout = Layout()
    right_layout.split(Layout(name="optimizations"), Layout(name="core_usage"))

    # This will be used in the next step for the adaptive algorithm
    opts_text = data.get("optimizations_text", "Normal Mode")
    right_layout["optimizations"].update(
        Panel(opts_text, title="Active Optimizations", border_style="blue")
    )

    core_bars = Table.grid(expand=True)
    core_bars.add_column(style="yellow")
    core_bars.add_column(ratio=1)
    per_core_usage = data.get('per_core_usage', [])
    for i, usage in enumerate(per_core_usage):
        core_bars.add_row(f"Core {i}", Bar(total=100, completed=usage, style="yellow", complete_style="yellow"))

    right_layout["core_usage"].update(
        Panel(core_bars, title="Per-Core Usage", border_style="blue")
    )
    layout["right"].update(right_layout)
    return layout

def run_dashboard():
    """Runs the live dashboard."""
    try:
        profiler = RealTimeProfiler()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return

    with Live(generate_layout(profiler.get_cpu_usage()), screen=True, redirect_stderr=False) as live:
        try:
            while True:
                time.sleep(1)
                data = profiler.get_cpu_usage()

                # Simple adaptive algorithm proof of concept
                total_usage = data.get('total_usage', 0.0)
                if total_usage > 50.0:
                    data['optimizations_text'] = "[bold red]High-Performance Mode: ON[/bold red]"
                else:
                    data['optimizations_text'] = "[bold green]Normal Mode: ON[/bold green]"

                live.update(generate_layout(data))
        except KeyboardInterrupt:
            pass

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="CpuOptMonitor: An adaptive runtime optimization system for CPUs.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Starts the CpuOptMonitor dashboard.")
    start_parser.set_defaults(func=run_dashboard)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
