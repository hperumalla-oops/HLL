import unittest
from hyperloglog.core import HyperLogLog

class TestUnionOperation(unittest.TestCase):
    def setUp(self):
        self.hll1 = HyperLogLog(b=14)
        self.hll2 = HyperLogLog(b=14)
        for item in range(50):
            self.hll1.add(str(item))
        for item in range(30, 80):
            self.hll2.add(str(item))

    def test_merge_is_union(self):
        hll1 = HyperLogLog(b=14)
        hll2 = HyperLogLog(b=14)
        for item in range(50):
            hll1.add(str(item))
        for item in range(30, 80):
            hll2.add(str(item))
        # Copy hll1 and merge hll2 into it (simulate union)
        union_hll = HyperLogLog(b=14)
        for item in range(50):
            union_hll.add(str(item))
        union_hll.merge(hll2)
        # Resulting cardinality should be at least as large as either input
        self.assertGreaterEqual(union_hll.estimate(), max(hll1.estimate(), hll2.estimate()))


if __name__ == "__main__":
    unittest.main()