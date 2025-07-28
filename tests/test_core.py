'''to run without moving the hyerloglog folder use command
python -m unittest tests.test_core'''
import unittest
from hyperloglog.core import HyperLogLog

class TestCore(unittest.TestCase):
    def test_basic_add_and_estimate(self):
        hll = HyperLogLog(b=14)
        for i in range(1000):
            hll.add(f"item{i}")
        est = hll.estimate()
        self.assertTrue(900 < est < 1100)

if __name__ == "__main__":
    unittest.main()
