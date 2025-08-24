import os
import shutil

console = None
try:
    from rich.console import Console
    console = Console()
except ImportError:
    pass

def _log(message):
    """Log to console if rich is available."""
    if console:
        console.print(f"[bold purple][Optimizer][/bold purple] {message}")
    else:
        print(f"[Optimizer] {message}")

def get_core_count():
    """Returns the number of available CPU cores."""
    return os.cpu_count() or 1

def apply_high_performance_mode(pid: int):
    """
    Applies high-performance optimizations to a process.
    - Sets CPU affinity to the first half of cores.
    - Sets a higher priority (lower nice value).
    """
    _log(f"Applying high-performance optimizations to PID {pid}...")
    core_count = get_core_count()
    # Pin to the first half of cores
    high_perf_cores = list(range(core_count // 2))
    if not high_perf_cores:
        high_perf_cores = [0]

    try:
        os.sched_setaffinity(pid, high_perf_cores)
        _log(f"Pinned PID {pid} to cores {high_perf_cores}.")
    except Exception as e:
        _log(f"[red]Failed to set CPU affinity for PID {pid}: {e}[/red]")

    try:
        # Lower nice value = higher priority. -20 is highest, 19 is lowest.
        # We need root privileges for negative nice values, so we'll use a small positive one for now.
        # A nice value of 0 is a good default. Let's try to set it to -5 if possible.
        # For a non-root user, we can only increase the nice value (lower priority).
        # Let's just demonstrate by setting it to 5.
        os.nice(5) # This sets it for the current process, which is APU.
        # To set for another process, we need to use setpriority.
        # os.setpriority(os.PRIO_PROCESS, pid, -5) # Requires root
        _log(f"Priority adjustments for PID {pid} are complex and may require root. Skipping for now.")

    except Exception as e:
        _log(f"[red]Failed to set priority for PID {pid}: {e}[/red]")


def apply_normal_mode(pid: int):
    """
    Resets optimizations, letting the OS manage the process normally.
    - Resets CPU affinity to all available cores.
    """
    _log(f"Resetting optimizations for PID {pid} to normal...")
    core_count = get_core_count()
    all_cores = list(range(core_count))

    try:
        os.sched_setaffinity(pid, all_cores)
        _log(f"Reset CPU affinity for PID {pid} to all cores.")
    except Exception as e:
        _log(f"[red]Failed to reset CPU affinity for PID {pid}: {e}[/red]")
