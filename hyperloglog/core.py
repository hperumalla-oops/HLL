from .dense import DenseHyperLogLog
from .sparse import hll_estimate_sparse, dedupe_and_sort, SparseHyperLogLog

class HyperLogLog:
    def __init__(self, b=14, mode='dense'):
        self.b = b
        self.mode = mode
        if mode == 'dense':
            self.impl = DenseHyperLogLog(b)
            self.registers = self.impl.registers
        elif mode == 'sparse':
            self.impl = SparseHyperLogLog(b)     
        else:
            raise ValueError('Unknown mode: ' + str(mode))

    def add(self, item):
        self.impl.add(item)

    def estimate(self):
        return self.impl.estimate()
        
    def merge(self, hll2):
        if self.b != hll2.b:
            raise ValueError("Cannot merge HLLs with different precision (b) values")
        if self.mode == 'sparse':
            self._convert_to_dense();
        if hll2.mode == 'sparse':
            hll2._convert_to_dense()
                              
        m = 1 << self.b
        merged_registers = [ max(self.impl.registers[i], hll2.impl.registers[i]) for i in range(m) ]

        self.impl.registers = merged_registers

        return self.estimate()
