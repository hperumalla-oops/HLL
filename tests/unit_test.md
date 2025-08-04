# Unit Test Instructions

## Running All Tests

To run all unit tests in the tests folder, open a terminal in the project root directory and execute:

```bash
python -m unittest discover -s tests
```

This command will automatically discover and run all test files in the tests directory.

## Running a Specific Test File

To run a specific test file, use the following command from the project root:

```bash
python -m unittest tests.file_name
```

Replace `file_name` with the name of the test file (without the `.py` extension) you wish to run.

## Test Files

### test_accuracy.py -- *Accuracy of Estimation*
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
```bash
.
----------------------------------------------------------------------
Ran 1 test in 0.245s

OK
```

---

### test_compatibility.py -- *Type Compatibility*
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
<img width="940" height="164" alt="image" src="https://github.com/user-attachments/assets/2d89f622-52fb-421b-8fb6-8406bb251875" />

---

### test_core.py -- *Basic Functionality*
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
<img width="940" height="187" alt="image" src="https://github.com/user-attachments/assets/6910d514-ebc0-42e8-a74f-6a375bd218da" />

---

### test_performance.py -- *Performance Benchmark*
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
<img width="940" height="174" alt="image" src="https://github.com/user-attachments/assets/026bbd6c-6e63-4fba-bfab-7a44e8d2552c" />

---

### test_serialization.py -- *Serialization Round-trip*
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
<img width="940" height="170" alt="image" src="https://github.com/user-attachments/assets/d52b7624-95ee-44ae-8f06-5884b49ccc8d" />

## Test Summary

All tests validate different aspects of the HyperLogLog implementation:
- **Accuracy**: Large dataset estimation within 2% error
- **Compatibility**: Support for both string and byte inputs
- **Core Functionality**: Basic operations with 10% accuracy tolerance
- **Performance**: Fast insertion operations under 2 seconds for 10K items
- **Serialization**: Data persistence without accuracy loss
<img width="940" height="182" alt="image" src="https://github.com/user-attachments/assets/9f6286ef-39a2-4834-ba40-72b9a3ec6347" />
