from bisect import bisect_left
import math

from .constants import ALPHA_MM, THRESHOLD, rawEstimateData, biasData
from .bias_correction import bias_estimate
from .hash_utils import murmurhash64a

class SparseHyperLogLog:
    def __init__(self, b=14, sparse_threshold=None):
        self.b = b
        self.m = 1 << b
        self.sparse_threshold = sparse_threshold or (self.m // 4)
        self.sparse_registers = []
        self.is_sparse = True
        
    def add(self, item):
        if not self.is_sparse:
            return self._dense_add(item)
            
        hash_value = murmurhash64a(item)
        idx = hash_value >> (64 - self.b)
        w = (hash_value << self.b) & ((1 << 64) - 1)
        rho = self._rho(w, 64 - self.b)
        
        pos = bisect_left(self.sparse_registers, (idx, 0))
        
        if pos < len(self.sparse_registers) and self.sparse_registers[pos][0] == idx:
            current_rho = self.sparse_registers[pos][1]
            if rho > current_rho:
                self.sparse_registers[pos] = (idx, rho)
        else:
            self.sparse_registers.insert(pos, (idx, rho))
            
        if len(self.sparse_registers) > self.sparse_threshold:
            self._convert_to_dense()
    
    def _rho(self, w, max_bits):
        def clzll(x): return 64 - x.bit_length() if x != 0 else 64
        rho = clzll(w) + 1
        if rho == 64:
            while rho < (1 << 6):  
                w = murmurhash64a(str(w))
                addn = clzll(w) + 1
                rho += addn
        return rho
    
    def _convert_to_dense(self):
        """Convert from sparse to dense representation"""
        self.dense_registers = [0] * self.m
        
        for idx, rho in self.sparse_registers:
            self.dense_registers[idx] = rho
            
        self.sparse_registers = []
        self.is_sparse = False
    
    def _dense_add(self, item):
        """Add item using dense representation (after conversion)"""
        hash_value = murmurhash64a(item)
        idx = hash_value >> (64 - self.b)
        w = (hash_value << self.b) & ((1 << 64) - 1)
        rho = self._rho(w, 64 - self.b)
        self.dense_registers[idx] = max(self.dense_registers[idx], rho)
    
    def estimate(self):
        if self.is_sparse:
            return self._sparse_estimate()
        else:
            return self._dense_estimate()
    
    def _sparse_estimate(self):
        """Estimate cardinality using sparse representation"""
        m = self.m
        
        Z = m - len(self.sparse_registers)  # contribution from zero registers
        Z += sum(2.0 ** -rho for _, rho in self.sparse_registers)
        
        E = ALPHA_MM[self.b] / Z
        
        V = m - len(self.sparse_registers)
        
        if E <= THRESHOLD[self.b]:
            correction = bias_estimate(E, self.b)
            E -= correction
            if E < 0:
                E = 0
        
        if V > 0:
            H = m * math.log(m / V)
            if H <= THRESHOLD[self.b]:
                return H
                
        return E
    
    def _dense_estimate(self):
        """Estimate cardinality using dense representation (after conversion)"""
        m = self.m
        Z = sum(2.0 ** -r for r in self.dense_registers)
        E = ALPHA_MM[self.b] / Z
        V = self.dense_registers.count(0)
        
        if E <= THRESHOLD[self.b]:
            correction = bias_estimate(E, self.b)
            E -= correction
            if E < 0:
                E = 0
        
        if V > 0:
            H = m * math.log(m / V)
            if H <= THRESHOLD[self.b]:
                return H
                
        return E
