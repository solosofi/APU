import random
import time
from typing import Dict, Any, List

class MockDataProvider:
    """
    A class to provide mock data for the CpuOptMonitor dashboard.
    """
    def __init__(self):
        self.optimizations = [
            "AVX-512 Vectorization",
            "Sparse Matrix Transformation: CSR->BSR",
            "Cache-aware tiling: 256x256x64",
            "Loop Unrolling (Factor 4)",
            "Dynamic Prefetching",
        ]

    def get_mock_data(self) -> Dict[str, Any]:
        """
        Generates a dictionary of mock performance data.
        """
        core_usage = random.uniform(40.0, 90.0)

        return {
            "task": "tensor_multiplication",
            "core_usage": core_usage,
            "memory_bw": random.uniform(20.0, 60.0),
            "ipc": random.uniform(1.5, 4.0),
            "cache_hit_l1": random.uniform(95.0, 99.0),
            "cache_hit_l2": random.uniform(88.0, 96.0),
            "cache_hit_l3": random.uniform(85.0, 94.0),
            "power_consumption": random.uniform(100.0, 200.0),
            "gflops_per_watt": random.uniform(3.0, 5.0),
            "active_optimizations": random.sample(self.optimizations, k=random.randint(1, 3)),
            "per_core_usage": [random.uniform(0.0, core_usage) for _ in range(8)] # Simulate 8 cores
        }

if __name__ == '__main__':
    # For testing the mock data provider
    provider = MockDataProvider()
    while True:
        data = provider.get_mock_data()
        print(data)
        time.sleep(1)
