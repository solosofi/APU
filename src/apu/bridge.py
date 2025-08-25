import ctypes
import json
import os
from pathlib import Path
import numpy as np

# Define the path to the shared library.
LIB_PATH = Path(__file__).parent.parent.parent / "src" / "core" / "build" / "libcore.so"

class CoreBridge:
    """
    A class that interfaces with the C++ core shared library.
    """
    def __init__(self):
        if not LIB_PATH.exists():
            raise FileNotFoundError(f"Shared library not found at {LIB_PATH}. Please compile the C++ core first.")

        self._lib = ctypes.CDLL(str(LIB_PATH))

        # --- Profiler function definitions ---
        self._get_cpu_usage_json = self._lib.get_cpu_usage_json
        self._get_cpu_usage_json.restype = ctypes.c_char_p
        self._get_cpu_usage_json.argtypes = []

        # --- SpMV kernel function definition ---
        self._spmv_csr_cpp = self._lib.spmv_csr_cpp
        self._spmv_csr_cpp.restype = None
        self._spmv_csr_cpp.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS'),
            ctypes.c_int
        ]

    def get_cpu_usage(self) -> dict:
        """
        Calls the C++ profiler function and returns CPU usage data.
        """
        json_bytes = self._get_cpu_usage_json()
        json_string = json_bytes.decode('utf-8')
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from profiler", "raw": json_string}

    def spmv_csr_cpp(self, data, indices, indptr, vector, result):
        """
        Calls the C++ SpMV kernel.
        """
        num_rows = len(indptr) - 1
        # Ensure data types are correct before passing to C++
        data = np.ascontiguousarray(data, dtype=np.float64)
        indices = np.ascontiguousarray(indices, dtype=np.int32)
        indptr = np.ascontiguousarray(indptr, dtype=np.int32)
        vector = np.ascontiguousarray(vector, dtype=np.float64)

        self._spmv_csr_cpp(data, indices, indptr, vector, result, num_rows)
