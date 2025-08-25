import argparse
import time
import subprocess
import os
import numpy as np
import threading
import queue
from collections import deque

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

# --- Threaded Reader for Subprocess Output ---
def _reader_thread(stream, q):
    """Reads lines from a stream and puts them into a queue."""
    try:
        for line in iter(stream.readline, b''):
            q.put(line.decode('utf-8').strip())
    except Exception as e:
        # This can happen if the stream is closed abruptly
        pass
    finally:
        stream.close()


def generate_layout(data: dict) -> Layout:
    """Generates the layout for the dashboard."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main"),
        Layout(name="footer", size=8) # New panel for output
    )
    header_text = Text(data.get("title", "APU"), justify="center", style="bold magenta")
    layout["header"].update(header_text)
    layout["main"].split_row(Layout(name="left"), Layout(name="right", ratio=2))

    metrics_table = Table.grid(expand=True)
    metrics_table.add_column(style="cyan")
    metrics_table.add_column(justify="right", style="green")
    total_usage = data.get('total_usage', 0.0)
    metrics_table.add_row("Total CPU Usage:", f"{total_usage:.1f}%")

    if "pid" in data:
        metrics_table.add_row("Task PID:", f"{data['pid']}")
    if "ops_per_sec" in data:
        metrics_table.add_row("Operations/sec:", f"{data['ops_per_sec']:.2f}")

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

    # --- Footer for Task Output ---
    output_lines = data.get("output_lines", [])
    output_text = "\n".join(output_lines)
    layout["footer"].update(Panel(output_text, title="Task Output", border_style="green"))

    return layout

def run_supervised_task(command_args):
    """Launches and monitors a supervised task, applying CPU affinity."""
    if not command_args:
        console.print("[bold red]Error:[/bold red] No command provided to 'run'.")
        return

    try:
        bridge = CoreBridge()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}. Please compile the C++ core first.")
        return

    try:
        process = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, # Decode output as text
            bufsize=1 # Line-buffered
        )
        console.print(f"🚀 Started process [bold cyan]{process.pid}[/bold cyan] for command: `{' '.join(command_args)}`")
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Command not found: '{command_args[0]}'")
        return
    except Exception as e:
        console.print(f"[bold red]An unexpected error during process launch:[/bold red] {e}")
        return

    # --- Setup for threaded output reading ---
    output_q = queue.Queue()
    output_lines = deque(maxlen=10) # Store last 10 lines of output

    # Start threads to read stdout and stderr
    stdout_thread = threading.Thread(target=_reader_thread, args=(process.stdout, output_q))
    stderr_thread = threading.Thread(target=_reader_thread, args=(process.stderr, output_q))
    stdout_thread.start()
    stderr_thread.start()

    data = bridge.get_cpu_usage()
    data['title'] = "APU: Supervising External Task"
    data['pid'] = process.pid
    data['optimizations_text'] = "[bold green]Normal Mode[/bold green]"
    data['output_lines'] = list(output_lines)
    high_perf_mode_active = False

    with Live(generate_layout(data), screen=True, redirect_stderr=False, auto_refresh=False) as live:
        try:
            while process.poll() is None:
                time.sleep(1)

                # Drain the queue of any new output
                while not output_q.empty():
                    output_lines.append(output_q.get_nowait())

                data = bridge.get_cpu_usage()
                data['title'] = "APU: Supervising External Task"
                data['pid'] = process.pid
                data['output_lines'] = list(output_lines)

                total_usage = data.get('total_usage', 0.0)

                if total_usage > 50.0 and not high_perf_mode_active:
                    optimizer.apply_high_performance_mode(process.pid)
                    high_perf_mode_active = True
                elif total_usage <= 50.0 and high_perf_mode_active:
                    optimizer.apply_normal_mode(process.pid)
                    high_perf_mode_active = False

                if high_perf_mode_active:
                    data['optimizations_text'] = "[bold red]High-Performance Mode (CPU Affinity Set)[/bold red]"
                else:
                    data['optimizations_text'] = "[bold green]Normal Mode[/bold green]"

                live.update(generate_layout(data))
                live.refresh()

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user. Terminating process...[/yellow]")
            process.terminate()
        finally:
            # Clean up threads
            stdout_thread.join()
            stderr_thread.join()
            # Ensure optimizations are reset on exit
            if high_perf_mode_active:
                optimizer.apply_normal_mode(process.pid)

    console.print(f"\n✅ Process [bold cyan]{process.pid}[/bold cyan] finished.")


def run_spmv_demo():
    """Runs the SpMV demo, showcasing adaptive kernel switching."""
    try:
        bridge = CoreBridge()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}. Please compile the C++ core first.")
        return

    console.print("Setting up SpMV workload...")
    coo_matrix = create_sparse_matrix()
    vector = np.random.rand(coo_matrix.shape[0])
    optimized_spmv = optimizer.create_optimized_spmv(bridge)
    active_spmv_func = spmv_coo_py
    high_perf_mode_active = False

    data = bridge.get_cpu_usage()
    data['title'] = "APU: SpMV Optimization Demo"
    data['optimizations_text'] = "[bold yellow]Initializing...[/bold yellow]"
    data['ops_per_sec'] = 0.0

    with Live(generate_layout(data), screen=True, redirect_stderr=False) as live:
        iterations = 0
        loop_start_time = time.time()
        try:
            while True:
                result = active_spmv_func(coo_matrix, vector)
                iterations += 1
                elapsed_time = time.time() - loop_start_time
                if elapsed_time >= 1.0:
                    ops_per_sec = iterations / elapsed_time
                    data = bridge.get_cpu_usage()
                    data['title'] = "APU: SpMV Optimization Demo"
                    data['ops_per_sec'] = ops_per_sec
                    total_usage = data.get('total_usage', 0.0)

                    if total_usage > 40.0 and not high_perf_mode_active:
                        console.print("[bold red]High CPU usage detected! Switching to C++ kernel.[/bold red]")
                        active_spmv_func = optimized_spmv
                        high_perf_mode_active = True

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
    parser = argparse.ArgumentParser(description="APU: An adaptive runtime optimization system for CPUs.", formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a command under APU supervision (applies CPU affinity).")
    run_parser.add_argument("user_command", nargs=argparse.REMAINDER, help="The command to run.")
    run_parser.set_defaults(func=lambda args: run_supervised_task(args.user_command))

    # SpMV Demo command
    demo_parser = subparsers.add_parser("run-spmv-demo", help="Run the SpMV optimization demo (showcases kernel switching).")
    demo_parser.set_defaults(func=lambda args: run_spmv_demo())

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
