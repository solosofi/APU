import argparse
import time
import subprocess
import os
import numpy as np

from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.progress_bar import ProgressBar as Bar
from rich.text import Text

from apu.bridge import CoreBridge
import apu.optimizer as optimizer

# Import the sample workload
from .sample_spmv import create_sparse_matrix, spmv_coo_py

console = Console()

def generate_layout(data: dict) -> Layout:
    """Generates the layout for the dashboard."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main"),
    )
    header_text = Text("APU: SpMV Optimization Demo", justify="center", style="bold magenta")
    layout["header"].update(header_text)
    layout["main"].split_row(Layout(name="left"), Layout(name="right", ratio=2))

    metrics_table = Table.grid(expand=True)
    metrics_table.add_column(style="cyan")
    metrics_table.add_column(justify="right", style="green")
    total_usage = data.get('total_usage', 0.0)
    metrics_table.add_row("Total CPU Usage:", f"{total_usage:.1f}%")

    ops_sec = data.get('ops_per_sec', 0.0)
    metrics_table.add_row("Operations/sec:", f"{ops_sec:.2f}")

    layout["left"].update(Panel(metrics_table, title="Live Metrics", border_style="blue"))

    right_layout = Layout()
    right_layout.split(Layout(name="optimizations"), Layout(name="core_usage"))
    opts_text = data.get("optimizations_text", "---")
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

def run_spmv_demo():
    """Runs the SpMV demo, showcasing adaptive optimization."""
    try:
        bridge = CoreBridge()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}. Please compile the C++ core first.")
        return

    # --- Setup the workload and optimizer ---
    console.print("Setting up SpMV workload...")
    coo_matrix = create_sparse_matrix()
    vector = np.random.rand(coo_matrix.shape[0])

    # Get the optimized function from the optimizer module
    optimized_spmv = optimizer.create_optimized_spmv(bridge)

    # Start with the slow, un-optimized function
    active_spmv_func = spmv_coo_py
    high_perf_mode_active = False

    data = bridge.get_cpu_usage()
    data['optimizations_text'] = "[bold yellow]Initializing...[/bold yellow]"
    data['ops_per_sec'] = 0.0

    with Live(generate_layout(data), screen=True, redirect_stderr=False) as live:
        iterations = 0
        loop_start_time = time.time()

        try:
            while True:
                # Run one iteration of the workload
                result = active_spmv_func(coo_matrix, vector)
                iterations += 1

                # Update stats and dashboard periodically
                elapsed_time = time.time() - loop_start_time
                if elapsed_time >= 1.0:
                    ops_per_sec = iterations / elapsed_time

                    data = bridge.get_cpu_usage()
                    data['ops_per_sec'] = ops_per_sec

                    # The Adaptive Logic
                    total_usage = data.get('total_usage', 0.0)

                    if total_usage > 40.0 and not high_perf_mode_active:
                        console.print("[bold red]High CPU usage detected! Switching to C++ kernel.[/bold red]")
                        active_spmv_func = optimized_spmv
                        high_perf_mode_active = True

                    # (In a real scenario, you might switch back if usage drops,
                    # but for this demo, we'll stay in high-perf mode once activated)

                    if high_perf_mode_active:
                        data['optimizations_text'] = "[bold green]MODE: Fast C++ CSR Kernel[/bold green]"
                    else:
                        data['optimizations_text'] = "[bold yellow]MODE: Slow Python COO Kernel[/bold yellow]"

                    live.update(generate_layout(data))
                    iterations = 0
                    loop_start_time = time.time()

        except KeyboardInterrupt:
            pass

    console.print("\n✅ Demo finished.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="APU: An adaptive runtime optimization system for CPUs.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # SpMV Demo command
    demo_parser = subparsers.add_parser("run-spmv-demo", help="Run the SpMV optimization demo.")
    demo_parser.set_defaults(func=lambda args: run_spmv_demo())

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
