import matplotlib.pyplot as plt
import time
import random
import string
from hyperloglog.core import HyperLogLog

# Range of values: 100 to 10 million
test_sizes = [10**x for x in range(2, 8)]  # 10^2 to 10^7

actual_values = []
estimated_values = []
error_percents = []
times = []

def generate_items(n):
    return [''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) for _ in range(n)]

for N in test_sizes:
    hll = HyperLogLog(b=14)
    items = generate_items(N)

    start = time.time()
    for item in items:
        hll.add(item)
    end = time.time()

    estimated = hll.estimate()
    error = abs(estimated - N) / N * 100
    elapsed = end - start

    actual_values.append(N)
    estimated_values.append(estimated)
    error_percents.append(error)
    times.append(elapsed)

    print(f"N={N} , Estimated={estimated}, Error={error:.4f}%, Time={elapsed:.2f}s")

# Plot True vs Estimated
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.plot(actual_values, actual_values, linestyle='--', label='True Value')
plt.plot(actual_values, estimated_values, marker='o', label='Estimated')
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Actual Count")
plt.ylabel("Estimated Count")
plt.title("True vs Estimated Cardinality")
plt.legend()
plt.grid(True)

# Plot Accuracy
plt.subplot(1, 3, 2)
plt.plot(actual_values, error_percents, marker='o', color='orange')
plt.xscale('log')
plt.xlabel("Actual Count")
plt.ylabel("Error (%)")
plt.title("Accuracy (Error %) vs True Count")
plt.grid(True)

# Plot Time
plt.subplot(1, 3, 3)
plt.plot(actual_values, times, marker='o', color='green')
plt.xscale('log')
plt.xlabel("Actual Count")
plt.ylabel("Time Taken (s)")
plt.title("Time vs Actual Count")
plt.grid(True)

plt.tight_layout()
plt.show()
