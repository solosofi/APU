import argparse
import time
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.progress_bar import ProgressBar as Bar
from rich.text import Text

from cpuoptmonitor.mock_data import MockDataProvider

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

    metrics_table = Table.grid(expand=True)
    metrics_table.add_column(style="cyan")
    metrics_table.add_column(justify="right", style="green")
    metrics_table.add_row("Task:", f"[bold]{data['task']}[/bold]")
    metrics_table.add_row("Core Usage:", f"{data['core_usage']:.1f}%")
    metrics_table.add_row("Memory BW:", f"{data['memory_bw']:.1f} GB/s")
    metrics_table.add_row("IPC:", f"{data['ipc']:.2f}")
    metrics_table.add_row("Cache Hit L1:", f"{data['cache_hit_l1']:.1f}%")
    metrics_table.add_row("Cache Hit L2:", f"{data['cache_hit_l2']:.1f}%")
    metrics_table.add_row("Cache Hit L3:", f"{data['cache_hit_l3']:.1f}%")
    metrics_table.add_row("Power:", f"{data['power_consumption']:.1f}W")
    metrics_table.add_row("Efficiency:", f"{data['gflops_per_watt']:.1f} GFLOPS/Watt")
    layout["left"].update(Panel(metrics_table, title="Live Metrics", border_style="blue"))

    right_layout = Layout()
    right_layout.split(Layout(name="optimizations"), Layout(name="core_usage"))
    opts_text = "\n".join(f"- {opt}" for opt in data['active_optimizations'])
    right_layout["optimizations"].update(
        Panel(opts_text, title="Active Optimizations", border_style="blue")
    )
    core_bars = Table.grid(expand=True)
    core_bars.add_column(style="yellow")
    core_bars.add_column(ratio=1)
    for i, usage in enumerate(data['per_core_usage']):
        core_bars.add_row(f"Core {i}", Bar(total=100, completed=usage, style="yellow", complete_style="yellow"))
    right_layout["core_usage"].update(
        Panel(core_bars, title="Per-Core Usage", border_style="blue")
    )
    layout["right"].update(right_layout)
    return layout

def run_dashboard():
    """Runs the live dashboard."""
    provider = MockDataProvider()
    with Live(generate_layout(provider.get_mock_data()), screen=True, redirect_stderr=False) as live:
        try:
            while True:
                time.sleep(1)
                live.update(generate_layout(provider.get_mock_data()))
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
