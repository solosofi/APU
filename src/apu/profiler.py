import ctypes
import json
import os
from pathlib import Path

# Define the path to the shared library.
# This assumes the script is run from the project root.
LIB_PATH = Path(__file__).parent.parent.parent / "src" / "core" / "build" / "libcore.so"

class RealTimeProfiler:
    """
    A class that interfaces with the C++ profiler shared library.
    """
    def __init__(self):
        if not LIB_PATH.exists():
            raise FileNotFoundError(f"Shared library not found at {LIB_PATH}. Please compile the C++ core first.")

        self._lib = ctypes.CDLL(str(LIB_PATH))

        # Define the function signature from the C++ library
        self._get_cpu_usage_json = self._lib.get_cpu_usage_json
        self._get_cpu_usage_json.restype = ctypes.c_char_p # The function returns a C-style string
        self._get_cpu_usage_json.argtypes = [] # The function takes no arguments

    def get_cpu_usage(self) -> dict:
        """
        Calls the C++ function and returns the CPU usage data as a Python dictionary.
        """
        json_bytes = self._get_cpu_usage_json()
        json_string = json_bytes.decode('utf-8')
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from profiler", "raw": json_string}

if __name__ == '__main__':
    # For testing the profiler bridge
    try:
        profiler = RealTimeProfiler()
        print("Successfully loaded the C++ profiler.")
        print("First reading (might be zero as it initializes):")
        print(profiler.get_cpu_usage())

        import time
        time.sleep(1)

        print("\nSecond reading (after 1 second):")
        print(profiler.get_cpu_usage())

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
