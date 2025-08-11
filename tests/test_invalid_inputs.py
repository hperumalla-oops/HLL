import unittest
from hyperloglog.core import HyperLogLog

class TestInvalidInputs(unittest.TestCase):
    def setUp(self):
        self.hll = HyperLogLog(b=14)

    def test_merge_with_none(self):
        with self.assertRaises(TypeError):
            self.hll.merge(None)

    def test_merge_with_string(self):
        with self.assertRaises(TypeError):
            self.hll.merge("invalid")

    def test_add_none(self):
        with self.assertRaises(TypeError):
            self.hll.add(None)

if __name__ == "__main__":
    unittest.main()
