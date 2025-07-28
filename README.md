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
from hyperloglog.core import HyperLogLog
from hyperloglog.serialization import serialize_hll, deserialize_hll

your_data=['apple', 'is', 'awesome','yaya','this','is','crazy','efee','feats','micorsoft','rejected','me','yesyes','hlolate','epsilon']

hll = HyperLogLog(b=14)  ##2^14 = 16384 buckets
for item in your_data:
    hll.add(item)

# Store in PostgreSQL
conn = psycopg2.connect(
        dbname="xx",  ##change
        user="postgres",
        password="xxxx", ###change
        host="localhost",
        port=5432)

cur = conn.cursor()


## Serialize to base64 for storage
serialized = serialize_hll(hll)
cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
        id SERIAL PRIMARY KEY,
        hll_data TEXT
    );
""")
conn.commit()

cur.execute("INSERT INTO analytics (hll_data) VALUES (%s)", (serialized,))
conn.commit()

cur.execute("SELECT hll_data FROM analytics ORDER BY id DESC LIMIT 1")
fetched_serialized = cur.fetchone()[0]

# Deserialize
binary = deserialize_hll(fetched_serialized)

print(f"Cardinality: {binary.estimate()}")
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
