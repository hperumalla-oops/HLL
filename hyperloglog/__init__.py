"""
HyperLogLog package initializer.

This package provides:
- HyperLogLog: The main class for cardinality estimation.
- serialize_hll / deserialize_hll: Safe Base64 serialization utilities.
"""
from .core import HyperLogLog
from .serialization import serialize_hll, deserialize_hll

__all__ = [
    "HyperLogLog",
    "serialize_hll",
    "deserialize_hll",
]
