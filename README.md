# CpuOptMonitor

CpuOptMonitor integrates an adaptive runtime optimization system to wrap the entire CPU in a feedback-driven optimization framework. This system dynamically applies sophisticated algorithms for tensor algebra, sparse matrix operations, and high-dimensional data handling, adapting in real-time to maximize compute-to-memory efficiency on general-purpose CPUs.

## How to Run

This project consists of a C++ core for profiling and a Python frontend for the dashboard.

**Note:** The current profiler reads from `/proc/stat`, so this application is intended for **Linux-based systems**.

### 1. Build the C++ Core

The C++ core must be compiled into a shared library first.

```bash
# Navigate to the core directory
cd src/core

# Create a build directory
mkdir build
cd build

# Run CMake to configure the project
cmake ..

# Compile the code
make
```

This will create a `libcore.so` file in the `src/core/build` directory.

### 2. Install Python Dependencies and the Application

From the **root** of the project directory, run the following command to install the Python dependencies and the `cpuoptmonitor` application in editable mode.

```bash
pip install -e .
```

### 3. Run the Dashboard

Once the C++ core is built and the Python package is installed, you can run the dashboard.

```bash
cpuoptmonitor start
```

The terminal will clear and display the live monitoring dashboard. Press `Ctrl+C` to exit.
