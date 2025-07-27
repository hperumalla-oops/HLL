from .dense import DenseHyperLogLog
from .sparse import hll_estimate_sparse, dedupe_and_sort

class HyperLogLog:
    def __init__(self, b=14, mode='dense'):
        self.b = b
        self.mode = mode
        if mode == 'dense':
            self.impl = DenseHyperLogLog(b)
        elif mode == 'sparse':
            # Placeholder: you can implement a SparseHyperLogLog class if needed
            raise NotImplementedError('Sparse mode not implemented as a class')
        else:
            raise ValueError('Unknown mode: ' + str(mode))

    def add(self, item):
        self.impl.add(item)

    def estimate(self):
        return self.impl.estimate()
        
    def merge(self, hll2):
        n = max(self.m, hll2.m)
        registers = []
        for i in range(n):
            registers.append(max(self.registers[i], hll2.registers[i]))
        self.registers = registers[:]
        return self.estimate()
