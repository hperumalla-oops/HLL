# import unittest
# from hyperloglog.core import HyperLogLog

# class TestUnionOperation(unittest.TestCase):
#     def setUp(self):
#         self.hll1 = HyperLogLog(b=14)
#         self.hll2 = HyperLogLog(b=14)
#         for item in range(50):
#             self.hll1.add(str(item))
#         for item in range(30, 80):
#             self.hll2.add(str(item))

#     def test_merge_is_union(self):
#         hll1 = HyperLogLog(b=14)
#         hll2 = HyperLogLog(b=14)
#         for item in range(50):
#             hll1.add(str(item))
#         for item in range(30, 80):
#             hll2.add(str(item))
#         # Copy hll1 and merge hll2 into it (simulate union)
#         union_hll = HyperLogLog(b=14)
#         for item in range(50):
#             union_hll.add(str(item))
#         union_hll.merge(hll2)
#         # Resulting cardinality should be at least as large as either input
#         self.assertGreaterEqual(union_hll.estimate(), max(hll1.estimate(), hll2.estimate()))

from hyperloglog.core import HyperLogLog
import unittest

class TestHLLMerge(unittest.TestCase):
    def setUp(self):
        self.precision = 5  # b=5 → 32 registers

    def _fill_hll(self, hll, start, end):
        """Helper: add integers as strings to the HLL."""
        for i in range(start, end):
            hll.add(str(i))
        return hll

    def _assert_merge_result(self, hll1, hll2):
        """Assert that merging increases or equals cardinality."""
        before_estimate = hll1.estimate()
        hll1.merge(hll2)
        after_estimate = hll1.estimate()
        self.assertGreaterEqual(after_estimate, before_estimate)

    def test_dense_dense_merge(self):
        h1 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 0, 50)
        h2 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 50, 100)
        result = h1.merge(h2)
        self.assertIs(result, h1)  # should return self
        self._assert_merge_result(h1, h2)

    def test_dense_sparse_merge(self):
        h1 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 0, 50)
        h2 = self._fill_hll(HyperLogLog(b=self.precision, mode="sparse"), 50, 100)
        result = h1.merge(h2)
        self.assertIs(result, h1)
        self._assert_merge_result(h1, h2)

    def test_sparse_dense_merge(self):
        h1 = self._fill_hll(HyperLogLog(b=self.precision, mode="sparse"), 0, 50)
        h2 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 50, 100)
        result = h1.merge(h2)
        self.assertIs(result, h1)
        self._assert_merge_result(h1, h2)

    def test_sparse_sparse_merge(self):
        h1 = self._fill_hll(HyperLogLog(b=self.precision, mode="sparse"), 0, 50)
        h2 = self._fill_hll(HyperLogLog(b=self.precision, mode="sparse"), 50, 100)
        result = h1.merge(h2)
        self.assertIs(result, h1)
        self._assert_merge_result(h1, h2)

    def test_chaining(self):
        h1 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 0, 25)
        h2 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 25, 50)
        h3 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 50, 75)
        h4 = self._fill_hll(HyperLogLog(b=self.precision, mode="dense"), 75, 100)

        # Chain merges: should still return self
        result = h1.merge(h2).merge(h3).merge(h4)
        self.assertIs(result, h1)
        # self.assertGreaterEqual(h1.estimate(), 100)
        relative_error = round(abs(h1.estimate() - 100) / 100,2)
        self.assertLessEqual(relative_error, 0.03)  #iwth 3% accuracy

if __name__ == "__main__":
    unittest.main()


