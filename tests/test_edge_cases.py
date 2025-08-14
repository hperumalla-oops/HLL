import unittest
from hyperloglog.core import HyperLogLog

class TestEdgeCases(unittest.TestCase):
    def test_empty_hll(self):
        hll = HyperLogLog(b=14)
        est = hll.estimate()
        self.assertLessEqual(est, 1.0)

    def test_single_element(self):
        hll = HyperLogLog(b=14)
        hll.add("foo")
        est = hll.estimate()
        self.assertGreaterEqual(est, 1.0)
        self.assertLessEqual(est, 2.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
