import unittest
from hyperloglog.core import HyperLogLog

class TestSparseToDenseConversion(unittest.TestCase):
    def setUp(self):
        self.b = 8  # Use a smaller b for a manageable m
        self.m = 1 << self.b

    def make_sparse(self, sparse_entries=None):
        """Helper to create a sparse HLL with a dictionary."""
        hll = HyperLogLog(b=self.b, mode='sparse')
        if sparse_entries:
            # CORRECT: Assigns a dictionary
            hll.impl.registers = sparse_entries.copy()
        return hll

    def test_sparse_to_dense_on_merge(self):
        # Create enough entries to exceed the sparse threshold
        threshold = self.m // 4
        many_entries = {i: (i % 7) + 1 for i in range(threshold + 5)}
        
        hll1 = self.make_sparse(many_entries)
        # CORRECTED: Use a dictionary for the second HLL
        hll2 = self.make_sparse({1: 15, 3: 12, 7: 9})

        # Sanity check: starts as sparse
        self.assertEqual(hll1.mode, 'sparse')

        hll1.merge(hll2)
        
        # After merge, it should have converted to dense
        self.assertEqual(hll1.mode, 'dense')

if __name__ == "__main__":
    unittest.main()