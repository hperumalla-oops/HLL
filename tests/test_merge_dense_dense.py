import unittest
from hyperloglog.core import HyperLogLog

class TestMergeDenseDense(unittest.TestCase):
    def setUp(self):
        self.b = 14
        self.m = 1 << self.b

    def make_dense(self, values=None):
        hll = HyperLogLog(b=self.b, mode='dense')
        if values:
            full_values = values + [0] * (self.m - len(values))
            hll.registers = full_values.copy()
            hll.impl.registers = full_values.copy()
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

if __name__ == "__main__":
    unittest.main()