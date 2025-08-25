# APU: Adaptive Runtime Optimizer

APU is an adaptive runtime optimization system that wraps your commands in a feedback-driven optimization framework. It monitors system performance in real-time and dynamically applies OS-level optimizations to your running processes to improve performance.

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

From the **root** of the project directory, run the following command to install the Python dependencies and the `apu` application in editable mode.

```bash
pip install -e .
```

### 3. Run a Command with APU

Once the C++ core is built and the Python package is installed, you can use `apu` to run and optimize any command.

The main command is `apu run`. It will launch your command, monitor system performance, and apply optimizations automatically.

**Example:**

To run a simple command like `stress` (you may need to install it: `sudo apt-get install stress`) and watch APU work, use:

```bash
# This will run a process that uses 1 CPU core at 100%
apu run stress -c 1
```

While this is running, the APU dashboard will show you the live CPU usage and which optimization mode is active. Press `Ctrl+C` to exit.
