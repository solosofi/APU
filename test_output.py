import time
import sys

print("--- Test Script Starting ---")
sys.stdout.flush()

for i in range(10):
    print(f"Line {i+1}: This is a test output line.")
    sys.stdout.flush() # Ensure output is not buffered
    time.sleep(0.5)

print("--- Test Script Finished ---")
sys.stdout.flush()
