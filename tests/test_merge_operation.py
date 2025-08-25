
from hyperloglog.core import HyperLogLog
import unittest


class TestMergeOperations(unittest.TestCase):
    def setUp(self):
        self.b = 5  # Small value for faster tests
        self.m = 1 << self.b

    def _fill_hll(self, hll, start, end):
        """Helper: add integers as strings to the HLL."""
        for i in range(start, end):
            hll.add(str(i))
        return hll

    def _make_dense(self, values=None):
        """Create a dense HLL with optional register values."""
        hll = HyperLogLog(b=self.b, mode='dense')
        if values:
            full_values = values + [0] * (self.m - len(values))
            hll.registers = full_values.copy()
            hll.impl.registers = full_values.copy()
        return hll

    def _make_sparse(self, sparse_entries=None):
        """Create a sparse HLL with optional sparse entries."""
        hll = HyperLogLog(b=self.b, mode='sparse')
        if sparse_entries:
            hll.registers = sparse_entries.copy()
            hll.impl.registers = sparse_entries.copy()
        return hll

    def _assert_merge_result(self, hll1, hll2):
        """Assert that merging increases or equals cardinality."""
        before_estimate = hll1.estimate()
        result = hll1.merge(hll2)
        after_estimate = hll1.estimate()
        self.assertIs(result, hll1)  # should return self
        self.assertGreaterEqual(after_estimate, before_estimate)

    def test_dense_dense_merge(self):
        hll1 = self._make_dense([1, 2, 3, 4])
        hll2 = self._make_dense([2, 3, 1, 5])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        result = hll1.merge(hll2)

        expected = [max(a, b) for a, b in zip(hll1.registers, hll2.registers)]
        self.assertEqual(hll1.impl.registers, expected)
        self.assertIs(result, hll1)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

    def test_dense_sparse_merge(self):
        hll1 = self._make_dense([1, 2, 3, 4])
        hll2 = self._make_sparse([(0, 7), (1, 1), (3, 2)])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        result = hll1.merge(hll2)

        expected = hll1.registers.copy()
        for idx, rho in hll2.registers:
            expected[idx] = max(expected[idx], rho)
        self.assertEqual(hll1.impl.registers, expected)
        self.assertIs(result, hll1)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

    def test_sparse_dense_merge(self):
        hll1 = self._make_sparse([(0, 2), (2, 1), (4, 5)])
        hll2 = self._make_dense([5, 2, 7, 1])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        result = hll1.merge(hll2)

        expected = [0] * self.m
        for idx, rho in [(0, 2), (2, 1), (4, 5)]:
            expected[idx] = rho
        for i in range(self.m):
            expected[i] = max(expected[i], hll2.registers[i])

        self.assertEqual(hll1.impl.registers, expected)
        self.assertIs(result, hll1)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

    def test_sparse_sparse_merge(self):
        hll1 = self._make_sparse([(0, 4), (3, 2), (6, 5)])
        hll2 = self._make_sparse([(0, 6), (2, 7), (3, 1)])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        result = hll1.merge(hll2)

        deduped = {}
        for idx, rho in hll1.registers + hll2.registers:
            if idx not in deduped or rho > deduped[idx]:
                deduped[idx] = rho
        expected_sparse = sorted(deduped.items())

        if hll1.mode == 'sparse':
            self.assertEqual(hll1.registers, expected_sparse)
        else:  # converted to dense
            dense_expected = [0] * self.m
            for idx, rho in expected_sparse:
                dense_expected[idx] = rho
            self.assertEqual(hll1.impl.registers, dense_expected)

        self.assertIs(result, hll1)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

    def test_merge_chaining(self):
        """Test that merge operations can be chained."""
        h1 = self._fill_hll(HyperLogLog(b=self.b, mode="dense"), 0, 25)
        h2 = self._fill_hll(HyperLogLog(b=self.b, mode="dense"), 25, 50)
        h3 = self._fill_hll(HyperLogLog(b=self.b, mode="dense"), 50, 75)
        h4 = self._fill_hll(HyperLogLog(b=self.b, mode="dense"), 75, 100)

        result = h1.merge(h2).merge(h3).merge(h4)
        self.assertIs(result, h1)
        
        # Check accuracy within reasonable error bounds
        relative_error = abs(h1.estimate() - 100) / 100
        self.assertLessEqual(relative_error, 0.2)  # 20% error tolerance

    def test_sparse_to_dense_conversion_on_merge(self):
        """Test that sparse HLL converts to dense when it gets too large."""
        # Use a larger b value for this test to ensure conversion happens
        large_b = 8  # 256 registers
        large_m = 1 << large_b
        
        # Create enough entries to definitely force conversion (beyond typical threshold)
        many_entries = [(i, i % 7 + 1) for i in range(large_m)]  # Fill all registers
        hll1 = HyperLogLog(b=large_b, mode='sparse')
        hll1.registers = many_entries.copy()
        hll1.impl.registers = many_entries.copy()
        
        hll2 = HyperLogLog(b=large_b, mode='sparse')
        hll2.registers = [(1, 15), (3, 12), (7, 9)]
        hll2.impl.registers = [(1, 15), (3, 12), (7, 9)]

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        result = hll1.merge(hll2)

        # After merge with many entries, should convert to dense
        self.assertEqual(hll1.mode, 'dense')
        self.assertIs(result, hll1)
        self.assertGreaterEqual(hll1.estimate(), max(card1_pre, card2_pre))

if __name__ == "__main__":
    unittest.main(verbosity=2)


