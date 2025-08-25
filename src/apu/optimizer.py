import os
import shutil
import numpy as np

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

# --- OS-Level Optimizations ---

def get_core_count():
    """Returns the number of available CPU cores."""
    return os.cpu_count() or 1

def apply_high_performance_mode(pid: int):
    """Applies CPU affinity optimization."""
    _log(f"Applying CPU affinity to PID {pid}...")
    core_count = get_core_count()
    high_perf_cores = list(range(core_count // 2))
    if not high_perf_cores:
        high_perf_cores = [0]

    try:
        os.sched_setaffinity(pid, high_perf_cores)
        _log(f"Pinned PID {pid} to cores {high_perf_cores}.")
    except Exception as e:
        _log(f"[red]Failed to set CPU affinity for PID {pid}: {e}[/red]")

def apply_normal_mode(pid: int):
    """Resets CPU affinity."""
    _log(f"Resetting CPU affinity for PID {pid} to normal...")
    core_count = get_core_count()
    all_cores = list(range(core_count))

    try:
        os.sched_setaffinity(pid, all_cores)
        _log(f"Reset CPU affinity for PID {pid} to all cores.")
    except Exception as e:
        _log(f"[red]Failed to reset CPU affinity for PID {pid}: {e}[/red]")


# --- Workload-Specific Optimizations ---

def create_optimized_spmv(bridge):
    """
    This is a function factory. It creates and returns an optimized SpMV function
    that is linked to the C++ core via the provided bridge.
    """
    _log("Creating optimized SpMV kernel function.")

    def spmv_optimized(coo_matrix, vector):
        """
        This function performs the actual optimization:
        1. Converts data layout from COO to CSR.
        2. Calls the high-performance C++ kernel.
        """
        # 1. Convert COO to CSR
        csr_matrix = coo_matrix.tocsr()

        # Prepare arrays for C++
        data = csr_matrix.data
        indices = csr_matrix.indices
        indptr = csr_matrix.indptr
        result = np.zeros(coo_matrix.shape[0], dtype=np.float64)

        # 2. Call the C++ kernel via the bridge
        bridge.spmv_csr_cpp(data, indices, indptr, vector, result)

        return result

    return spmv_optimized
