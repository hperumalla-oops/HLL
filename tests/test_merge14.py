import unittest
from hyperloglog.core import HyperLogLog

class TestHyperLogLogMerge(unittest.TestCase):

    def setUp(self):
        # Use b=14 so ALPHA_MM/THRESHOLD are available
        self.b = 14
        self.m = 1 << self.b

    def make_dense(self, values=None):
        hll = HyperLogLog(b=self.b, mode='dense')
        if values:
            # Fill up to m registers
            full_values = values + [0] * (self.m - len(values))
            hll.registers = full_values.copy()
            hll.impl.registers = full_values.copy()
        return hll

    def make_sparse(self, sparse_entries=None):
        hll = HyperLogLog(b=self.b, mode='sparse')
        if sparse_entries:
            hll.registers = sparse_entries.copy()
            hll.impl.registers = sparse_entries.copy()
        return hll

    def test_merge_dense_dense(self):
        hll1 = self.make_dense([1, 2, 3, 4])
        hll2 = self.make_dense([2, 3, 1, 5])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        res_card = hll1.merge(hll2)

        expected = [max(a, b) for a, b in zip(hll1.registers, hll2.registers)]
        self.assertEqual(hll1.impl.registers, expected)
        self.assertGreaterEqual(res_card, max(card1_pre, card2_pre))

    def test_merge_dense_sparse(self):
        hll1 = self.make_dense([1, 2, 3, 4])
        hll2 = self.make_sparse([(0, 7), (1, 1), (3, 2)])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        res_card = hll1.merge(hll2)

        expected = hll1.registers.copy()
        for idx, rho in hll2.registers:
            expected[idx] = max(expected[idx], rho)
        self.assertEqual(hll1.impl.registers, expected)
        self.assertGreaterEqual(res_card, max(card1_pre, card2_pre))

    def test_merge_sparse_dense(self):
        hll1 = self.make_sparse([(0, 2), (2, 1), (4, 5)])
        hll2 = self.make_dense([5, 2, 7, 1])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        res_card = hll1.merge(hll2)

        expected = [0] * self.m
        for idx, rho in [(0, 2), (2, 1), (4, 5)]:
            expected[idx] = rho
        for i in range(self.m):
            expected[i] = max(expected[i], hll2.registers[i])

        self.assertEqual(hll1.impl.registers, expected)
        self.assertGreaterEqual(res_card, max(card1_pre, card2_pre))

    def test_merge_sparse_sparse(self):
        hll1 = self.make_sparse([(0, 4), (3, 2), (6, 5)])
        hll2 = self.make_sparse([(0, 6), (2, 7), (3, 1)])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        res_card = hll1.merge(hll2)

        deduped = {}
        for idx, rho in hll1.registers + hll2.registers:
            if idx not in deduped or rho > deduped[idx]:
                deduped[idx] = rho
        expected_sparse = sorted(deduped.items())

        if hll1.mode == 'sparse':
            self.assertEqual(hll1.registers, expected_sparse)
        else:
            dense_expected = [0] * self.m
            for idx, rho in expected_sparse:
                dense_expected[idx] = rho
            self.assertEqual(hll1.impl.registers, dense_expected)

        self.assertGreaterEqual(res_card, max(card1_pre, card2_pre))

    def test_merge_sparse_sparse_dense_conversion(self):
        many_entries = [(i, i % 7 + 1) for i in range(int(self.m * 0.9))]
        hll1 = self.make_sparse(many_entries)
        hll2 = self.make_sparse([(1, 15), (3, 12), (7, 9)])

        card1_pre = hll1.estimate()
        card2_pre = hll2.estimate()
        res_card = hll1.merge(hll2)

        self.assertEqual(hll1.mode, 'dense')
        expected = [0] * self.m
        for idx, rho in many_entries + hll2.registers:
            expected[idx] = max(expected[idx], rho)
        self.assertEqual(hll1.impl.registers, expected)
        self.assertGreaterEqual(res_card, max(card1_pre, card2_pre))

    def test_merge_different_b_should_raise(self):
        hll1 = HyperLogLog(b=14)
        hll2 = HyperLogLog(b=15)
        with self.assertRaises(ValueError):
            hll1.merge(hll2)

if __name__ == "__main__":
    unittest.main()
