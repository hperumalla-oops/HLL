from bisect import bisect_left
import math

from .constants import ALPHA_MM, THRESHOLD, rawEstimateData, biasData
from .bias_correction import bias_estimate
from .hash_utils import murmurhash64a

def dedupe_and_sort(sparse_data):
    """
    Remove duplicates and sort the sparse data array.
    Returns the deduped count and sorted array.
    """
    unique_data = sorted(set(sparse_data))
    return len(unique_data), unique_data

def hll_estimate_sparse(hloglog_b, hloglog_binbits, sparse_data, sparse_idx):
    """
    Evaluates the stored encoded hashes using linear counting.
    Args:
        hloglog_b: The 'b' parameter (number of index bits)
        hloglog_binbits: Number of bits per bin
        sparse_data: List of encoded hash values
        sparse_idx: Number of elements in sparse_data
    Returns:
        Cardinality estimate using linear counting
    """
    
    m = 2 ** (32 - 1 - hloglog_binbits)
    sparse_idx, sparse_data_deduped = dedupe_and_sort(sparse_data[:sparse_idx])
    V = 0
    
    for i in range(sparse_idx):
        if i == 0:
            V += 1
            
        elif sparse_data_deduped[i] != sparse_data_deduped[i-1]:
            V += 1
            
    V = sparse_idx
    if m - V <= 0:
        return float('inf')
        
    estimate = m * math.log(m / (m - V))
    return estimate


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
        self.registers = [0] * self.m
        
        for idx, rho in self.sparse_registers:
            self.registers[idx] = rho
            
        # self.sparse_registers = []
        self.is_sparse = False
    
    def _dense_add(self, item):
        """Add item using dense representation (after conversion)"""
        hash_value = murmurhash64a(item)
        idx = hash_value >> (64 - self.b)
        w = (hash_value << self.b) & ((1 << 64) - 1)
        rho = self._rho(w, 64 - self.b)
        self.registers[idx] = max(self.registers[idx], rho)
    
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
        Z = sum(2.0 ** -r for r in self.registers)
        E = ALPHA_MM[self.b] / Z
        V = self.registers.count(0)
        
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
