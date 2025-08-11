import unittest
from hyperloglog.core import HyperLogLog

class TestMergeDifferentB(unittest.TestCase):
    def test_different_b_raises(self):
        hll1 = HyperLogLog(b=14)
        hll2 = HyperLogLog(b=15)
        with self.assertRaises(ValueError):
            hll1.merge(hll2)

if __name__ == "__main__":
    unittest.main()
