from bisect import bisect_left
import math

from .constants import ALPHA_MM, THRESHOLD
from .bias_correction import bias_estimate
from .hash_utils import murmurhash64a
from .compression import decompress_sparse_registers

class SparseHyperLogLog:
    """
    Sparse HyperLogLog (HLL) implementation.

    Uses a sparse representation of registers (list of (index, rho)) 
    for small cardinalities. This reduces memory usage until a 
    threshold is reached, at which point switching to dense 
    representation is recommended.
    """
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
            # If registers are provided in compressed form, decompress them
            self.registers = decompress_sparse_registers(register, b)
        else:
            # Start with an empty sparse register set
            self.registers = []
        
    def add(self, item: object) -> int:
        """
        Adds an item to the HLL. Converts to dense if threshold exceeded.

        Args:
            item (object): Any hashable value; internally converted to string.

        Returns:
            int: 1 if sparse threshold exceeded (suggesting dense conversion), 0 otherwise.
        """

        # Compute hash and derive register index + rho value
        hash_value = murmurhash64a(item)
        idx = hash_value >> (64 - self.b)    # register index
        w = (hash_value << self.b) & ((1 << 64) - 1)    # suffix

        rho = self._rho(w, 64 - self.b)

        # Insert/update (idx, rho) in sorted register list
        pos = bisect_left(self.registers, (idx, 0))
        
        if pos < len(self.registers) and self.registers[pos][0] == idx:
            # Update if this rho is larger than existing
            current_rho = self.registers[pos][1]
            if rho > current_rho:
                self.registers[pos] = (idx, rho)
        else:
            # Insert new index-rho pair in sorted order
            self.registers.insert(pos, (idx, rho))

        # If too many registers filled, suggest dense conversion
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
        def clzll(x):     # count leading zeros
            return 64 - x.bit_length() if x != 0 else 64
        rho = clzll(w) + 1

        # Rare fallback: rehash if rho is too large (all zeros suffix)
        if rho >= 64:
            max_val = min(1 << 6, max_bits)  # cap with max_bits
            safety_counter = 0               
            while rho < max_val:
                w = murmurhash64a(str(w))
                addn = clzll(w) + 1
                if addn <= 0:
                    break  # avoid infinite loop
                rho += addn
                safety_counter += 1
                if safety_counter > max_bits:  # hard safety cutoff
                    break

        return min(rho, max_bits)
    
    
    def estimate(self) -> float:
        """
        Estimate cardinality using the sparse representation.

        Returns:
            float: Estimated number of distinct elements.
        """
        m = self.m
        
        Z = m - len(self.registers)  # contribution from zero registers
        Z += sum(2.0 ** -rho for _, rho in self.registers)

        # Raw estimate
        E = ALPHA_MM[self.b] / Z

        # Number of zeros (for linear counting)
        V = m - len(self.registers)

        # Apply bias correction for mid-range estimates
        if E <= THRESHOLD[self.b]:
            correction = bias_estimate(E, self.b)
            E -= correction
            if E < 0:
                E = 0

        # Use linear counting when many registers are still zero
        if V > 0:
            H = m * math.log(m / V)
            if H <= THRESHOLD[self.b]:
                return H
                
        return E
