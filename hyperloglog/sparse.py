from bisect import bisect_left
import math

from .constants import ALPHA_MM, THRESHOLD, rawEstimateData, biasData
from .bias_correction import bias_estimate
from .hash_utils import murmurhash64a
from .compression import decompress_sparse_registers



def hll_estimate_sparsedef hll_estimate_sparse(hloglog_b: int, hloglog_binbits: int, sparse_data: List[int], sparse_idx: int) -> float:
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
    def __init__(self, b: int = 14, register: int | bytes = 0, sparse_threshold: int | None = None):
        """
        Initialize a sparse HLL.

        Args:
            b (int): Precision parameter (number of bits for index). Default is 14.
            register (int | bytes): Encoded register data or 0 for empty. Default is 0.
            sparse_threshold (int | None): Threshold for switching to dense. Defaults to m // 4.
        """
        self.b = b
        self.m = 1 << b
        self.sparse_threshold = sparse_threshold or (self.m // 4)
        if register:
            self.registers = decompress_sparse_registers(register, b)
        self.registers = []
        
    def add(self, item: object) -> int:
        """
        Adds an item to the HLL. Converts to dense if threshold exceeded.

        Args:
            item (object): Any hashable value; internally converted to string.

        Returns:
            int: 1 if sparse threshold exceeded (suggesting dense conversion), 0 otherwise.
        """
           
        hash_value = murmurhash64a(item)
        idx = hash_value >> (64 - self.b)
        w = (hash_value << self.b) & ((1 << 64) - 1)
        rho = self._rho(w, 64 - self.b)
        
        pos = bisect_left(self.registers, (idx, 0))
        
        if pos < len(self.registers) and self.registers[pos][0] == idx:
            current_rho = self.registers[pos][1]
            if rho > current_rho:
                self.registers[pos] = (idx, rho)
        else:
            self.registers.insert(pos, (idx, rho))
            
        if len(self.registers) > self.sparse_threshold:
            return 1
        return 0
    
    def _rho(self, w: int, max_bits: int) -> int:
        """
        Computes the position of the first 1-bit (rho) in the hash suffix.

        Args:
            w (int): The suffix of the hash.
            max_bits (int): Maximum number of bits to examine.

        Returns:
            int: rho value (1-based index of first 1-bit).
        """
        def clzll(x): return 64 - x.bit_length() if x != 0 else 64
        rho = clzll(w) + 1
        if rho == 64:
            while rho < (1 << 6):  
                w = murmurhash64a(str(w))
                addn = clzll(w) + 1
                rho += addn
        return rho
    
    
    def estimate(self) -> float:
        """
        Estimate cardinality using the sparse representation.

        Returns:
            float: Estimated number of distinct elements.
        """
        m = self.m
        
        Z = m - len(self.registers)  # contribution from zero registers
        Z += sum(2.0 ** -rho for _, rho in self.registers)
        
        E = ALPHA_MM[self.b] / Z
        
        V = m - len(self.registers)
        
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
