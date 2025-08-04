
##  `hyperloglog/`

This directory contains all core components of the HLL logic.

---

## Files Overview

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

---

## `core.py`

### Class: `HyperLogLog`

Implements the probabilistic counting algorithm.

---

### 1. **`__init__(self, precision: int = 14)`**

**Inputs:**
- `precision` (`int`): Controls the size of the register array (number of buckets = `2^precision`). Higher precision gives more accuracy but uses more memory.

**Logic:**
- Initializes `m = 2^precision` registers.
- Uses the formula from the original HyperLogLog paper for alpha constant and raw estimation.


---

### 2. **`add(self, item: Union[str, int, bytes])`**

**Inputs:**
- `item`: Any hashable object. Internally converted to bytes and hashed.

**Logic:**
- Applies a hash function.
- Splits hash bits: prefix to determine register index, suffix to count leading zeroes.
- Updates the corresponding register.

---

### 3. **`count(self) -> int`**

**Returns:**
- Estimated number of unique elements.

**Math:**
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

## `serialization.py`

### `serialize_hll(hll: HyperLogLog) -> bytes`
- Converts HLL object into a byte stream for saving or transmission.

### `deserialize_hll(data: bytes) -> HyperLogLog`
- Reconstructs the HLL object from serialized bytes.

---

## `constants.py`

Check `constants.py` for values like:
- `ALPHA_CONSTANTS`: For bias correction.
- `MIN_PRECISION`, `MAX_PRECISION`: Allowed precision bounds.

---

## `dense.py`
- Implements dense mode for larger cardinalities.
- Uses bias correction and maintains full register array.
- Core function: `estimate()` applies correction logic based on threshold.

---

## `sparse.py`
- Efficient mode for smaller cardinalities.
- Stores `(index, rho)` pairs only.
- Automatically converts to dense when size exceeds threshold.

---

## `bias_correction.py`
- Function: `bias_estimate(E, b)`
- Interpolates between known raw estimates and bias values.

---

## `compression.py`
- `pack_registers(registers, binbits)` → bytes
- `unpack_registers(data, m, binbits)` → list[int]

---

## `hash_utils.py`
- `murmurhash64a(key, seed=0)`: Converts string or bytes to 64-bit hash.






# HyperLogLog (HLL) - Core Module Documentation

This module implements the **HyperLogLog (HLL)** algorithm in Python, which is used for **cardinality estimation** (i.e., estimating the number of distinct elements in a dataset) with **low memory usage**.

---

## 📁 Directory: `hyperloglog/`

This directory contains all core components of the HLL logic.

---

## 🔧 Files Overview

| Module | Description |
|--------|-------------|
| `core.py` | High-level API for creating, updating, and estimating cardinality using HLL. |
| `dense.py` | Handles dense register representation (used at higher cardinalities). |
| `sparse.py` | Handles sparse encoding (used at lower cardinalities). |
| `bias_correction.py` | Applies empirical bias correction to improve HLL accuracy. |
| `compression.py` | Converts between sparse and dense formats efficiently. |
| `serialization.py` | Provides serialization/deserialization support for HLL objects. |
| `hash_utils.py` | Utility functions for hashing, bit manipulations, and index extraction. |
| `constants.py` | Contains constants like thresholds, alpha values, and bias tables. |
| `__init__.py` | Makes this a Python package. |

---

## 📘 core.py - Detailed Documentation

### 🔹 Overview
This module defines the HyperLogLog class, the primary interface for approximate cardinality estimation in this implementation. It wraps around two internal implementations:

DenseHyperLogLog (from dense.py)

SparseHyperLogLog (from sparse.py)

The class automatically handles switching between sparse and dense representations based on the number of inserted elements, optimizing for both accuracy and memory efficiency.

### ⚙️ Initialization
hll = HyperLogLog(b=14, mode='sparse', register=0)

b: Precision parameter. m = 2^b defines the number of registers (default is 14, i.e., 16,384 registers).

mode: Either 'sparse' or 'dense'.

register: Initial register state (default is 0).




