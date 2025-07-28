'''to run without moving the hyerloglog folder use command
python -m unittest tests.test_accuracy'''
import unittest
from hyperloglog.core import HyperLogLog

class TestAccuracy(unittest.TestCase):
    def test_large_cardinality(self):
        hll = HyperLogLog(b=14)
        for i in range(50000):
            hll.add(f"item{i}")
        est = hll.estimate()
        self.assertTrue(abs(est - 50000) / 50000 < 0.02)  # <2% error

if __name__ == "__main__":
    unittest.main()
