# APU: Adaptive Runtime Optimizer

APU is an adaptive runtime optimization system that wraps your commands in a feedback-driven optimization framework. It monitors system performance in real-time and dynamically applies optimizations to your running processes to improve performance.

## How It Works

APU uses a C++ core to monitor system-wide CPU usage in real-time. Based on this profiling, it can apply two different kinds of optimizations:

1.  **OS-Level Optimization:** For any generic command, APU can apply CPU affinity to pin the process to a dedicated set of cores, which can improve cache performance.
2.  **Workload-Specific Optimization:** For known, high-performance tasks, APU can perform more advanced optimizations, such as switching out a slow algorithm for a highly-optimized C++ kernel at runtime.

## Commands

There are two main commands to use APU:

### 1. `apu run <command>`

This command runs any arbitrary command under APU's supervision.

-   **Optimization Applied:** CPU Affinity.
-   **How it works:** When APU detects high system-wide CPU usage, it will automatically pin your command's process to the first half of the available CPU cores to improve performance. When the load decreases, it will remove the affinity setting.
-   **Use this for:** Running your own scripts or general-purpose programs to get a potential performance boost from CPU affinity.

**Example:**
```bash
# Run a CPU stress test and watch APU apply CPU affinity
apu run stress -c 1
```

### 2. `apu run-spmv-demo`

This command runs a built-in demonstration of a much more powerful, workload-specific optimization.

-   **Optimization Applied:** Adaptive Kernel Switching.
-   **How it works:** The demo runs a sparse matrix-vector multiplication (SpMV) task. It starts with a slow, pure-Python implementation. When APU detects the high CPU load from this, it **swaps the Python function with a highly-optimized C++ kernel** at runtime.
-   **Use this for:** Seeing a clear and dramatic demonstration of APU's advanced capabilities. The dashboard will show the "Operations / Second" metric skyrocketing when the C++ kernel is activated.

## How to Build and Run

**Note:** This application is intended for **Linux-based systems**.

### 1. Build the C++ Core
```bash
# From the project root, configure and build the C++ core
cmake -S src/core -B src/core/build
make -C src/core/build
```

### 2. Install the Application
```bash
# From the project root, install the Python package
pip install -e .
```

### 3. Run a Command
```bash
# Run the generic optimizer on your own command
apu run <your command>

# Or, run the advanced SpMV demo
apu run-spmv-demo
```
The terminal will clear and display the live monitoring dashboard. Press `Ctrl+C` to exit.
