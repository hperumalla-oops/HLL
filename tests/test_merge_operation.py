from hyperloglog.core import HyperLogLog
import unittest

class TestMergeOperations(unittest.TestCase):
    def setUp(self):
        self.b = 5
        self.m = 1 << self.b

    def _make_dense(self, values=None):
        hll = HyperLogLog(b=self.b, mode='dense')
        if values:
            full_values = values + [0] * (self.m - len(values))
            hll.impl.registers = full_values.copy()
        return hll

    def _make_sparse(self, sparse_entries=None):
        """Helper to create a sparse HLL with a dictionary."""
        hll = HyperLogLog(b=self.b, mode='sparse')
        if sparse_entries:
            # CORRECT: Assigns a dictionary
            hll.impl.registers = sparse_entries.copy()
        return hll

    def test_dense_sparse_merge(self):
        hll1 = self._make_dense([1, 2, 3, 4])
        # CORRECTED: Use a dictionary for sparse data
        hll2 = self._make_sparse({0: 7, 1: 1, 3: 2})

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        hll1.merge(hll2)

        expected = hll1.impl.registers.copy()
        for idx, rho in hll2.impl.registers.items():
            expected[idx] = max(expected[idx], rho)
        self.assertEqual(hll1.impl.registers, expected)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

    def test_sparse_dense_merge(self):
        # CORRECTED: Use a dictionary for sparse data
        hll1 = self._make_sparse({0: 2, 2: 1, 4: 5})
        hll2 = self._make_dense([5, 2, 7, 1])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        hll1.merge(hll2)

        expected_sparse = {0: 2, 2: 1, 4: 5}
        expected_dense = [0] * self.m
        for idx, rho in expected_sparse.items():
            expected_dense[idx] = rho
        for i in range(self.m):
            expected_dense[i] = max(expected_dense[i], hll2.impl.registers[i])

        self.assertEqual(hll1.impl.registers, expected_dense)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

    def test_sparse_sparse_merge(self):
        # CORRECTED: Use dictionaries for sparse data
        hll1 = self._make_sparse({0: 4, 3: 2, 6: 5})
        hll2 = self._make_sparse({0: 6, 2: 7, 3: 1})

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        hll1.merge(hll2)

        expected = {0: 6, 2: 7, 3: 2, 6: 5}
        self.assertEqual(hll1.impl.registers, expected)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

if __name__ == "__main__":
    unittest.main(verbosity=2)