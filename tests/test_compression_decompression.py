import unittest
# CORRECTED: Import the specific implementation classes needed for the test
from hyperloglog.core import HyperLogLog
from hyperloglog.dense import DenseHyperLogLog
from hyperloglog.sparse import SparseHyperLogLog
from hyperloglog.compression import pack_registers, compress_sparse_registers

class TestCompression(unittest.TestCase):
    def test_dense_packing_roundtrip(self):
        hll = HyperLogLog(b=14, mode='dense')
        for i in range(100):
            hll.add(str(i))
        
        # CORRECTED: Access hll.impl.registers and use 6 bits for packing
        self.assertIsInstance(hll.impl, DenseHyperLogLog)
        data = pack_registers(hll.impl.registers, 6)
        self.assertIsInstance(data, bytes)

    def test_sparse_compression_roundtrip(self):
        hll = HyperLogLog(b=14, mode='sparse')
        for i in range(5):
            hll.add(str(i))
            
        # CORRECTED: Access hll.impl.registers
        self.assertIsInstance(hll.impl, SparseHyperLogLog)
        data = compress_sparse_registers(hll.impl.registers, hll.b)
        self.assertIsInstance(data, bytes)

if __name__ == '__main__':
    unittest.main(verbosity=2)