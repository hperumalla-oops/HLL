# HyperLogLog Implementation in Python

A high-performance Python implementation of the HyperLogLog probabilistic cardinality estimator, based on the PostgreSQL HLL extension.

##  Features

- **Sparse & Dense Encoding**
- **High Accuracy**
- **PostgreSQL Compatible**
- **Compression Support**
- **Set Operations**
- **Serialization**
  
## Installation

```bash
git clone https://github.com/hperumalla-oops/HLL.git
cd HLL
pip install -e .
```

##  Quick Start

```python
from hyperloglog.core import HyperLogLog

hll = HyperLogLog()

true=100000
# Add elements
for i in range(true):
    hll.add(f"user_{i}")

print(f"True unique users:",true)
print(f"Estimated unique users: {hll.estimate()}")
print("accuracy:", 1-((hll.estimate()-true)/true))

hll2 = HyperLogLog()
for i in range(50000, 150000):
    hll2.add(f"user_{i}")

merged = hll.merge(hll2)
print("Union estimate:",merged)
```

## Database Integration

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
### Examples provided
```bash
cd examples
py python database_storage.py --dbname dbname --user postgres --password pwd --host localhost --port 5432
```


### Core Classes

#### `HyperLogLog`
Main HLL counter class with automatic sparse-to-dense conversion.

**Parameters:**
- `b` (int): Number of index bits (4-18). Defualt: 14.
   (Higher = more accurate but more memory)
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
