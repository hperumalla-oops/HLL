"""
HyperLogLog package init.
"""
from .dense import DenseHyperLogLog
from .sparse import hll_estimate_sparse, dedupe_and_sort
