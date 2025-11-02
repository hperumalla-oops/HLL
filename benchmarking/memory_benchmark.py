import matplotlib.pyplot as plt
import random
import string
from hyperloglog import HyperLogLog
import tracemalloc


# Range of values: 100 to 10 million
test_sizes = [10**x for x in range(2, 8)]  # 10^2 to 10^7

actual_values = []
memory_usages_kb = []

def generate_items(n):
    return [''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) for _ in range(n)]

# Run HLL benchmarking
for N in test_sizes:
    hll = HyperLogLog(b=14)
    items = generate_items(N)

    tracemalloc.start()

    for item in items:
        hll.add(item)

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    memory_usages_kb.append(peak / 1024)  # Convert to kilobytes
    actual_values.append(N)
    print(f"Cardinality: {N}, Peak Memory Usage: {peak / 1024:.2f} KB")


    estimated = hll.estimate()
    error = abs(estimated - N) / N * 100

# Plot cardinality vs memory 
plt.figure(figsize=(10, 6))
plt.plot(actual_values, memory_usages_kb, marker='o', linestyle='-', color='purple')
plt.title("Memory Usage vs True Cardinality")
plt.xlabel("True Cardinality (Number of Unique Elements)")
plt.ylabel("Peak Memory Usage (KB)")
plt.xscale('log')
plt.grid(True)
plt.show()
