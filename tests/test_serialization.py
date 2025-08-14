'''to run without moving the hyerloglog folder use command
python -m unittest tests.test_serialization'''
import unittest
from hyperloglog.core import HyperLogLog
from hyperloglog.serialization import serialize_hll, deserialize_hll

class TestSerialization(unittest.TestCase):
    def test_round_trip(self):
        hll = HyperLogLog(b=14)
        for i in range(1000):
            hll.add(f"item{i}")
        b64 = serialize_hll(hll)
        hll2 = deserialize_hll(b64)
        self.assertAlmostEqual(hll.estimate(), hll2.estimate(), delta=1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
