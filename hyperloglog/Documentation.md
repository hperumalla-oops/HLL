# HyperLogLog (HLL) - Core Module Documentation

This module implements the **HyperLogLog (HLL)** algorithm in Python, which is used for **cardinality estimation** (i.e., estimating the number of distinct elements in a dataset) with **low memory usage**.

---

## 📁 Directory: `hyperloglog/`

This directory contains all core components of the HLL logic.

---

## 🔧 Files Overview

| File               | Description |
|--------------------|-------------|
| `core.py`          | Main implementation of the HyperLogLog algorithm. Includes initialization, update, and estimation methods. |
| `serialization.py` | Functions to serialize/deserialize HLL objects for storage and transmission. |
| `__init__.py`      | Initializes the package module. |
| `constants.py`     | Contains algorithm-specific constants like bias correction values or default precision. |
| `utils.py` (if any)| Helper functions used across modules (hashing, bucket processing, etc.). |

---

## 📘 core.py - Detailed Documentation

### 🔹 Class: `HyperLogLog`

Implements the probabilistic counting algorithm.

---

### 1. **`__init__(self, precision: int = 14)`**

**Inputs:**
- `precision` (`int`): Controls the size of the register array (number of buckets = `2^precision`). Higher precision gives more accuracy but uses more memory.

**Logic (Math Behind):**
- Initializes `m = 2^precision` registers.
- Uses the formula from the original HyperLogLog paper for alpha constant and raw estimation.

**Edge Handling:**
- Precision values are bounded (commonly between 4 and 18). Errors raised for invalid inputs.

---

### 2. **`add(self, item: Union[str, int, bytes])`**

**Inputs:**
- `item`: Any hashable object. Internally converted to bytes and hashed.

**Logic:**
- Applies a hash function.
- Splits hash bits: prefix to determine register index, suffix to count leading zeroes.
- Updates the corresponding register.

**Edge Cases:**
- Handles different input types (str, int, bytes).
- Ignores empty or null inputs with warnings or skips.

---

### 3. **`count(self) -> int`**

**Returns:**
- Estimated number of unique elements.

**Math Behind:**
- Applies raw estimate:
  \[
  E = \alpha_m \cdot m^2 \cdot \left(\sum_{j=1}^{m} 2^{-M[j]}\right)^{-1}
  \]
- Applies bias correction and linear counting in small ranges.

**Edge Handling:**
- Returns 0 if no elements added.
- Handles overflow and underflow cases using corrections.

---

### 4. **`merge(self, other: HyperLogLog)`**

**Inputs:**
- Another HLL instance with the same precision.

**Logic:**
- Element-wise maximum merge of registers.

**Edge Handling:**
- Throws error if precision differs.

---

## 🧪 Serialization Functions

### `serialize_hll(hll: HyperLogLog) -> bytes`
- Converts HLL object into a byte stream for saving or transmission.

### `deserialize_hll(data: bytes) -> HyperLogLog`
- Reconstructs the HLL object from serialized bytes.

---

## 🧮 Constants

Check `constants.py` for values like:
- `ALPHA_CONSTANTS`: For bias correction.
- `MIN_PRECISION`, `MAX_PRECISION`: Allowed precision bounds.

---

## 📌 Edge Case Handling Summary

| Case | Handling |
|------|----------|
| No elements added | Returns 0 estimate |
| Invalid precision | Raises `ValueError` |
| Incompatible merge | Raises error |
| Large inputs | Handled by hashing |
| Duplicate inputs | Ignored by nature of HLL |

---

## 🧪 Example Usage

```python
from hyperloglog.core import HyperLogLog

hll = HyperLogLog(precision=14)
hll.add("apple")
hll.add("banana")
print(hll.count())  # Output: ~2





