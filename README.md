# HyperLogLog Implementation in Python

A high-performance Python implementation of the HyperLogLog probabilistic cardinality estimator, based on the PostgreSQL HLL extension. For python >= 9.10

## Features

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

## Quick Start

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
print("Union estimate:",merged.estimate())
```

## Core Classes

### `HyperLogLog`
Main HLL counter class with automatic sparse-to-dense conversion.

**Parameters:**
- `b` (int): Number of index bits (4-18). Default: 14.
   (Higher = more accurate but more memory)
- `mode` (str): dense or sparse. Default: dense

**Methods:**
- `add(item: str)`: Add element to counter
- `estimate() -> float`: Get cardinality estimate
- `merge(other: HyperLogLog) -> HyperLogLog`: Merge with another counter

## Architecture Overview

The `hyperloglog/` directory contains all core components of the HLL logic.

### Files Overview

| File                | Description |
|---------------------|-------------|
| `core.py`           | Main interface for the HyperLogLog algorithm.
| `dense.py`          | Dense mode implementation using a full register array and bias-corrected estimation. |
| `sparse.py`         | Sparse mode implementation for low cardinalities with compact memory usage. |
| `bias_correction.py`| Interpolates bias correction based on precomputed lookup data. |
| `compression.py`    | Provides register packing/unpacking into compact byte formats. |
| `constants.py`      | Defines constants like `ALPHA_MM`, thresholds, and bias correction tables. |
| `serialization.py`  | Serializes and deserializes HLL objects using `pickle` and `base64`. |
| `hash_utils.py`     | Implements MurmurHash64A to hash input items consistently and uniformly. |

### `core.py`

#### Class: `HyperLogLog`

Implements the probabilistic counting algorithm.

#### 1. **`__init__(self, precision: int = 14)`**

**Inputs:**
- `precision` (`int`): Controls the size of the register array (number of buckets = `2^precision`). Higher precision gives more accuracy but uses more memory.

**Logic:**
- Initializes `m = 2^precision` registers.
- Uses the formula from the original HyperLogLog paper for alpha constant and raw estimation.

#### 2. **`add(self, item: Union[str, int, bytes])`**

**Inputs:**
- `item`: Any hashable object. Internally converted to bytes and hashed.

**Logic:**
- Applies a hash function.
- Splits hash bits: prefix to determine register index, suffix to count leading zeroes.
- Updates the corresponding register.

#### 3. **`count(self) -> int`**

**Returns:**
- Estimated number of unique elements.

**Math:**
- Applies raw estimate:
    Raw Estimation Formula:
    E = αₘ × m² × ( ∑(j=1 to m) 2^(-M[j]) )^(-1)
    
    Where:
    - m = 2^b is the number of registers
    - M[j] is the value in the j-th register
    - αₘ is a constant depending on m

- Applies bias correction and linear counting in small ranges.

**Edge Handling:**
- Returns 0 if no elements added.
- Handles overflow and underflow cases using corrections.

#### 4. **`merge(self, other: HyperLogLog)`**

**Inputs:**
- Another HLL instance with the same precision.

**Logic:**
- Element-wise maximum merge of registers.

**Edge Handling:**
- Throws error if precision differs.

### `serialization.py`

#### `serialize_hll(hll: HyperLogLog) -> bytes`
- Converts HLL object into a byte stream for saving or transmission.

#### `deserialize_hll(data: bytes) -> HyperLogLog`
- Reconstructs the HLL object from serialized bytes.

### `constants.py`

Check `constants.py` for values like:
- `ALPHA_CONSTANTS`: For bias correction.
- `MIN_PRECISION`, `MAX_PRECISION`: Allowed precision bounds.

### `dense.py`
- Implements dense mode for larger cardinalities.
- Uses bias correction and maintains full register array.
- Core function: `estimate()` applies correction logic based on threshold.

### `sparse.py`
- Efficient mode for smaller cardinalities.
- Stores `(index, rho)` pairs only.
- Automatically converts to dense when size exceeds threshold.

### `bias_correction.py`
- Function: `bias_estimate(E, b)`
- Interpolates between known raw estimates and bias values.

### `compression.py`
- `pack_registers(registers, binbits)` → bytes
- `unpack_registers(data, m, binbits)` → list[int]

### `hash_utils.py`
- `murmurhash64a(key, seed=0)`: Converts string or bytes to 64-bit hash.

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

### PostgreSQL Setup

```python
conn = psycopg2.connect(
    dbname="hll_test",  # <- change this
    user="postgres",
    password="AIML",  # <- change this
    host="localhost",
    port=5432
)
```

Tables are auto-created via:

```sql
CREATE TABLE hll_counters (
    label TEXT,
    hll_data TEXT
);
```

## Example Usage

### `examples/basic_usage.py`

Demonstrates:
- Creating HLLs from labeled datasets.
- Estimating cardinalities.
- Storing and retrieving HLLs from a PostgreSQL table using base64 serialization.
- Validating that estimates remain consistent after database round-trips.

#### To run:
```bash
python -m examples.basic_usage
```

#### Key behavior:
- Four sample datasets (`fruits`, `nuts`, `animals`, `people`) are stored and fetched.
- Estimates before and after storage are compared.
- Uses `serialize_hll()` and `deserialize_hll()` to handle DB-friendly HLL formats.

### `examples/database_storage.py`

Demonstrates:
- Creating a high-precision HLL (`b=14`) for 50,000 items.
- Estimating cardinality.
- Creating the necessary PostgreSQL table schema.

#### To run:
```bash
python -m examples.database_storage
```

## Unit Testing

### Running All Tests

To run all unit tests in the tests folder, open a terminal in the project root directory and execute:

```bash
python -m unittest discover -s tests
```

This command will automatically discover and run all test files in the tests directory.

### Running a Specific Test File

To run a specific test file, use the following command from the project root:

```bash
python -m unittest tests.file_name
```

Replace `file_name` with the name of the test file (without the `.py` extension) you wish to run.

### Test Files

#### test_accuracy.py -- *Accuracy of Estimation*
```python
import unittest
from hyperloglog.core import HyperLogLog

class TestAccuracy(unittest.TestCase):
    def test_large_cardinality(self):
        hll = HyperLogLog(b=14)
        for i in range(50000):
            hll.add(f"item{i}")
        est = hll.estimate()
        self.assertTrue(abs(est - 50000) / 50000 < 0.02)  # <2% error

if __name__ == "__main__":
    unittest.main()

```

**Purpose:**  
Validates that the HyperLogLog estimator produces accurate cardinality estimates for large datasets.

**Key Test:**
- Inserts 50,000 unique items
- Checks that the estimated count is within **2% error** of the true count

**Documentation line:**  
Ensures HyperLogLog maintains high accuracy (<2% error) on large datasets (50K items).

**Output:**
```bash
.
----------------------------------------------------------------------
Ran 1 test in 0.245s

OK
```

#### test_compatibility.py -- *Type Compatibility*
```python
import unittest
from hyperloglog.core import HyperLogLog

class TestCompatibility(unittest.TestCase):
    def test_string_and_bytes(self):
        hll = HyperLogLog(b=14)
        hll.add("foo")
        hll.add(b"foo")  # Should not raise, but may hash differently
        self.assertIsInstance(hll.estimate(), float)

if __name__ == "__main__":
    unittest.main()
```

**Purpose:**  
Verifies that HyperLogLog handles both str and bytes inputs without raising errors.

**Key Test:**
- Adds both "foo" (string) and b"foo" (bytes)
- Confirms that the estimation process still works

**Documentation line:**  
Confirms compatibility for both string and byte inputs; type flexibility is supported.

**Output:**
```bash
.
----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

#### test_core.py -- *Basic Functionality*
```python
import unittest
from hyperloglog.core import HyperLogLog

class TestCore(unittest.TestCase):
    def test_basic_add_and_estimate(self):
        hll = HyperLogLog(b=14)
        for i in range(1000):
            hll.add(f"item{i}")
        est = hll.estimate()
        self.assertTrue(900 < est < 1100)

if __name__ == "__main__":
    unittest.main()
```

**Purpose:**  
Tests core functionality: adding elements and estimating cardinality.

**Key Test:**
- Inserts 1,000 unique items
- Asserts that estimate falls within expected range (±10%)

**Documentation line:**  
Tests basic add-and-estimate logic; ensures accurate count for smaller datasets (1K items).

**Output:**
```bash
.
----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
```

#### test_performance.py -- *Performance Benchmark*
```python
import unittest
import time
from hyperloglog.core import HyperLogLog

class TestPerformance(unittest.TestCase):
    def test_speed(self):
        hll = HyperLogLog(b=14)
        start = time.time()
        for i in range(10000):
            hll.add(f"item{i}")
        elapsed = time.time() - start
        self.assertLess(elapsed, 2.0)  # Should be fast

if __name__ == "__main__":
    unittest.main()
```

**Purpose:**  
Measures the speed of insertion operations in HyperLogLog.

**Key Test:**
- Adds 10,000 items and asserts it completes in under **2 seconds**

**Documentation line:**  
Validates performance by ensuring insertions of 10K items stay under 2 seconds.

**Output:**
```bash
.
----------------------------------------------------------------------
Ran 1 test in 0.050s

OK
```

#### test_serialization.py -- *Serialization Round-trip*
```python
import unittest
from hyperloglog.core import HyperLogLog
from hyperloglog.serialization import serialize_hll, deserialize_hll

class TestSerialization(unittest.TestCase):
    def test_round_trip(self):
        hll = HyperLogLog(b=14)
        for i in range(1000):
            hll.add(f"item{i}")
        b64 = serialize_hll(hll)
        hll2 = deserialize_hll(b64)
        self.assertAlmostEqual(hll.estimate(), hll2.estimate(), delta=1)

if __name__ == "__main__":
    unittest.main()
```

**Purpose:**  
Ensures HyperLogLog can be serialized and deserialized without losing accuracy.

**Key Test:**
- Serializes an HLL with 1,000 items
- Deserializes and confirms estimates from both are nearly identical (within ±1)

**Documentation line:**  
Checks serialization/deserialization round-trip preserves estimation with minimal deviation.

**Output:**
```bash
.
----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

### Test Summary

All tests validate different aspects of the HyperLogLog implementation:
- **Accuracy**: Large dataset estimation within 2% error
- **Compatibility**: Support for both string and byte inputs
- **Core Functionality**: Basic operations with 10% accuracy tolerance
- **Performance**: Fast insertion operations under 2 seconds for 10K items
- **Serialization**: Data persistence without accuracy loss

**Output:**
```bash
.....
----------------------------------------------------------------------
Ran 5 tests in 0.332s

OK
```

## Notes

- Merge only HLLs with the same `b` value.
- You can inspect the first 10 registers for debug using:
  ```python
  hll.impl.registers[:10]
  ```
