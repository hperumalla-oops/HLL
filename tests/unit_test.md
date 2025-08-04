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
<img width="900" height="400" alt="image" src="https://github.com/user-attachments/assets/ebd7df8a-0213-4e68-a7f9-ab18854c8718" />

**Purpose:**  
Validates that the HyperLogLog estimator produces accurate cardinality estimates for large datasets.

**Key Test:**
- Inserts 50,000 unique items
- Checks that the estimated count is within **2% error** of the true count

**Documentation line:**  
Ensures HyperLogLog maintains high accuracy (<2% error) on large datasets (50K items).
<img width="940" height="182" alt="image" src="https://github.com/user-attachments/assets/ad0da1a8-c233-4e09-8dde-c34d0b306e82" />

---

### test_compatibility.py -- *Type Compatibility*
<img width="900" height="410" alt="image" src="https://github.com/user-attachments/assets/e5228127-d3c4-4718-92d2-708ebbc90309" />

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
<img width="686" height="509" alt="image" src="https://github.com/user-attachments/assets/65f55367-1ed6-4ab9-85bb-55c67111f0b1" />

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
<img width="853" height="577" alt="image" src="https://github.com/user-attachments/assets/d7b696dc-ec65-43bb-a2d2-c5fbcf09d008" />

**Purpose:**  
Measures the speed of insertion operations in HyperLogLog.

**Key Test:**
- Adds 10,000 items and asserts it completes in under **2 seconds**

**Documentation line:**  
Validates performance by ensuring insertions of 10K items stay under 2 seconds.
<img width="940" height="174" alt="image" src="https://github.com/user-attachments/assets/026bbd6c-6e63-4fba-bfab-7a44e8d2552c" />

---

### test_serialization.py -- *Serialization Round-trip*
<img width="940" height="505" alt="image" src="https://github.com/user-attachments/assets/240abd9f-9675-4874-bbfd-98a8ca2f9346" />

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
