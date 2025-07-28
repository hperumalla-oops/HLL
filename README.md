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
## Unit Test Instructions

### Running All Tests
To run all unit tests in the tests folder, open a terminal in the project root directory and execute:
```bash
python -m unittest discover -s tests
```
### Running a Specific Test File
To run a specific test file, use the following command from the project root:
```bash
python -m unittest tests.test_accuracy
```

## Database Integration

### PostgreSQL Example
```python
import psycopg2
from hyperloglog.core import HyperLogLog
from hyperloglog.serialization import serialize_hll, deserialize_hll
COLUMN_NAME = ''
TABLE_NAME = ''
# Store in PostgreSQL
conn = psycopg2.connect(
        dbname="xx",  ##change
        user="postgres",
        password="xxxx", ###change
        host="localhost",
        port=5432)

cur = conn.cursor()
query = f"SELECT {COLUMN_NAME} FROM {TABLE_NAME}"
cur.execute(query)
rows = cur.fetchall()

hll = HyperLogLog(b=14)  ##2^14 = 16384 buckets
for item in your_data:
    hll.add(item)
print(f"Cardinality: {hll.estimate()}")
cur.execute("""
    CREATE TABLE IF NOT EXISTS hll_snapshots (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cardinality INT,
        compressed_registers BYTEA
    );
""")
conn.commit()
cur.execute("""
    INSERT INTO hll_snapshots (cardinality, compressed_registers)
    VALUES (%s, %s)
""", (hll.estimate, hll.store()))

conn.commit()
cur.close()
conn.close()
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


