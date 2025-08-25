import time
import numpy as np
from scipy.sparse import random as sparse_random

# --- Workload Definition ---
# This section defines the data and the slow/fast functions for our task.
# In a real application, this would be the user's code.

def create_sparse_matrix(size=2000, density=0.01):
    """Creates a large, random sparse matrix in COO format."""
    print(f"Creating a {size}x{size} sparse matrix with {density*100}% density...")
    S = sparse_random(size, size, density=density, format='coo', dtype=np.float64)
    print("Matrix created.")
    return S

def spmv_coo_py(coo_matrix, vector):
    """
    A slow, pure-Python implementation of Sparse Matrix-Vector multiplication
    for a matrix in COO format.
    """
    result = np.zeros(coo_matrix.shape[0], dtype=np.float64)
    for i, j, v in zip(coo_matrix.row, coo_matrix.col, coo_matrix.data):
        result[i] += v * vector[j]
    return result

# --- APU Integration Point ---
# The APU system will override this dictionary with optimized functions
# when High-Performance Mode is active.
WORKLOAD_FUNCTIONS = {
    "spmv": spmv_coo_py
}

def get_workload_function(name):
    """The task will call this to get the currently active function."""
    return WORKLOAD_FUNCTIONS[name]


# --- Main Task Loop ---
# This is the main loop of the user's task.
def main():
    matrix_size = 2000
    coo_matrix = create_sparse_matrix(size=matrix_size)
    vector = np.random.rand(matrix_size)

    print("\nStarting workload loop. Press Ctrl+C to stop.")
    iterations = 0
    start_time = time.time()

    while True:
        try:
            # Get the currently active SpMV function
            spmv_func = get_workload_function("spmv")

            # Execute the function
            result = spmv_func(coo_matrix, vector)

            iterations += 1
            elapsed_time = time.time() - start_time
            if elapsed_time >= 2: # Print stats every 2 seconds
                ops_per_sec = iterations / elapsed_time
                # This print statement is for the user running the script directly.
                # The APU dashboard will provide a cleaner view.
                print(f"  - Performance: {ops_per_sec:.2f} ops/sec")
                iterations = 0
                start_time = time.time()

        except KeyboardInterrupt:
            print("\nWorkload stopped.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == '__main__':
    main()
