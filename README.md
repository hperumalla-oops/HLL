# HyperLogLog Implementation in Python

A high-performance Python implementation of the HyperLogLog probabilistic cardinality estimator, based on the PostgreSQL HLL extension.

##  Features

- **Sparse & Dense Encoding**: Automatically switches from memory-efficient sparse to dense representation
- **High Accuracy**: Implements bias correction and linear counting for small cardinalities
- **PostgreSQL Compatible**: Binary format compatible with PostgreSQL HLL extension
- **Compression Support**: Multiple compression algorithms for storage efficiency
- **Set Operations**: Union, intersection, complement operations on HLL counters
- **Serialization**: Base64 encoding for database storage

## 🔧 Installation

```bash
pip install hyperloglog-python
```

Or from source:
```bash
git clone https://github.com/yourusername/hyperloglog-python
cd hyperloglog-python
pip install -r requirments.txt
```

## 📖 Quick Start

```python
from hyperloglog import HyperLogLog

hll = HyperLogLog()

# Add elements
for i in range(100000):
    hll.add(f"user_{i}")

# Get cardinality estimate
print(f"Estimated unique users: {hll.estimate()}")

# Merge with another counter
hll2 = HyperLogLog(error_rate=0.01)
for i in range(50000, 150000):
    hll2.add(f"user_{i}")

merged = hll.merge(hll2)
print(f"Union estimate: {merged.estimate()}")
```

## 🗄️ Database Integration

### PostgreSQL Example
```python
import psycopg2
from hyperloglog import HyperLogLog

# Create and populate HLL
hll = HyperLogLog(b=14)  # 2^14 = 16384 buckets
for item in your_data:
    hll.add(item)

# Store in PostgreSQL
conn = psycopg2.connect("your_connection_string")
cur = conn.cursor()

# Serialize to base64 for storage
serialized = hll.to_base64()
cur.execute("INSERT INTO analytics (hll_data) VALUES (%s)", (serialized,))

# Load from database
cur.execute("SELECT hll_data FROM analytics WHERE id = %s", (1,))
loaded_hll = HyperLogLog.from_base64(cur.fetchone()[0])
print(f"Cardinality: {loaded_hll.estimate()}")
```


### Core Classes

#### `HyperLogLog`
Main HLL counter class with automatic sparse-to-dense conversion.

**Parameters:**
- `b` (int): Number of index bits (4-18). Defualt: 14. (Higher = more accurate but more memory)
- `mode` (str): dense or sparse. Defualt: dense

**Methods:**
- `add(item: str)`: Add element to counter
- `estimate() -> float`: Get cardinality estimate
- `merge(other: HyperLogLog) -> HyperLogLog`: Merge with another counter


### Set Operations

```python
# Union (|)
union_count = hll1 | hll2

# Intersection (&)  
intersection_count = hll1 & hll2

# Difference (-)
difference_count = hll1 - hll2

# Symmetric difference (^)
sym_diff_count = hll1 ^ hll2
```
