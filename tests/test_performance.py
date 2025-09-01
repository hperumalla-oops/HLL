'''to run without moving the hyerloglog folder use command
python -m unittest tests.test_performance'''
import unittest
import time
from hyperloglog.core import HyperLogLog

class TestPerformance(unittest.TestCase):
    def test_speed(self):
        hll = HyperLogLog(b=14)
        start = time.time()
        for i in range(10000):
            hll.add(f"item{i}")
        elapsed = time.time() - start
        self.assertLess(elapsed, 2.0)  # Should be fast

if __name__ == "__main__":
    unittest.main(verbosity=2)
