from .dense import DenseHyperLogLog
from .sparse import hll_estimate_sparse, dedupe_and_sort, SparseHyperLogLog
from .compression import pack_registers, compress_sparse_registers

class HyperLogLog:
    def __init__(self, b=14, mode='sparse', register=0):
        self.b = b # number of bits in the register
        self.mode = mode # dense or sparse 
        self.m = 1 << b
        self.dontbefore = False
        if mode == 'dense':
            self.impl = DenseHyperLogLog(b, register)
        elif mode == 'sparse':
            self.impl = SparseHyperLogLog(b, register)           
        else:
            raise ValueError('Unknown mode: ' + str(mode))
        self.registers = self.impl.registers

    def add(self, item):
        if (self.impl.add(str(item))):
            print("Converting to Dense")
            registers = [0] * self.m
            for idx, rho in self.registers:
                registers[idx] = rho
            self.registers = registers
            self.convert_to_dense()

    def estimate(self):
        return self.impl.estimate()

    def storing(self):
        if self.mode == 'dense':
            return pack_registers(self.registers, self.b)
        else:
            return compress_sparse_registers(self.registers, self.b )

    def convert_to_dense(self):
        self.mode = 'dense'
        self.impl = DenseHyperLogLog(self.b, self.storing())
        self.registers = self.impl.registers

    def merge(self, hll2):
        if self.b != hll2.b:
            raise ValueError("Cannot merge HLLs with different precision (b) values")
        if self.mode == 'sparse':
            print("Converting to Dense")
            self._convert_to_dense()

        if hll2.mode == 'sparse':
            hll2._convert_to_dense()
                              
        m = 1 << self.b
        merged_registers = [ max(self.impl.registers[i], hll2.impl.registers[i]) for i in range(m) ]

        self.impl.registers = merged_registers

        return self.estimate()


