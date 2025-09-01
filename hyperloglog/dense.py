import math

from .constants import ALPHA_MM, THRESHOLD
from .bias_correction import bias_estimate
from .hash_utils import murmurhash64a
from .compression import unpack_registers

class DenseHyperLogLog:
    """
    Dense HyperLogLog implementation .
    """
    def __init__(self, b: int = 14, register: int | bytes = 0):
        """
        Initializes the DenseHyperLogLog instance.

        Args:
            b (int): Precision parameter (number of bits for indexing registers). Default is 14.
            register (int or bytes): Packed register state or 0 for a fresh instance.

        Notes:
            - The number of registers m is 2^b.
            - If `register` is provided, it is unpacked into register values.
        """
        self.b=b
        self.m = 1 << b # number of registers
        if register:
            # Unpack provided serialized register state
            self.registers = unpack_registers(register, self.m, 6)
        else:
            # Fresh empty registers
            self.registers = [0] * self.m

    def add(self, item: str) -> int:
        """
        Adds a single item to the HLL estimator.

        Args:
            item (str): The item to add (already stringified externally).

        Returns:
            int: Always returns 0 (placeholder for compatibility with sparse mode).
        """
        # Hash input with 64-bit murmurhash
        hash_value = murmurhash64a(item)
        # Split hash into register index (first b bits) and remainder (w)
        idx = hash_value >> (64 - self.b)
        w = (hash_value << self.b) & ((1 << 64) - 1)
        # Compute rho = position of first set bit + 1
        rho = self._rho(w, 64 - self.b)
        # Update register with max observed rho for this index
        self.registers[idx] = max(self.registers[idx], rho)
        return 0

    def _rho(self, w: int, max_bits: int) -> int:
        """
        Computes the position of the first set bit (rho value) in the hash, adjusted for noise.

        Args:
            w (int): The hashed value.
            max_bits (int): The maximum number of bits allowed.

        Returns:
            int: The rho value, capped at `max_bits`.

        Notes:
            - Implements a fallback re-hashing loop if rho is suspiciously large.
        """
        # Count leading zeros (clz)
        def clzll(x): return 64 - x.bit_length() if x != 0 else 64
        rho = clzll(w) + 1
        
        if rho >= 64:
            # Safety: if rho maxes out, keep rehashing to avoid extreme skew
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
        Estimates the cardinality of the current multiset based on register values.

        Returns:
            float: The estimated number of unique elements.

        Notes:
            - Applies raw HyperLogLog formula for large cardinalities.
            - Uses bias correction for mid-range estimates.
            - Uses linear counting for small cardinalities with many zero registers.
        """
        m = self.m
        # Raw harmonic mean estimate (HLL formula)
        Z = sum(2.0 ** -r for r in self.registers)
        E = ALPHA_MM[self.b] / Z
        # Count empty registers (needed for small-cardinality correction)
        V = self.registers.count(0)
        # Bias correction for small/mid range
        if E <= THRESHOLD[self.b]:
            correction = bias_estimate(E, self.b)
            E -= correction
            if E < 0:
                E = 0
        # Linear counting for small cardinalities (many empty registers)
        if V > 0:
            H = m * math.log(m / V)
            if H <= THRESHOLD[self.b]:
                return H
        # Otherwise, return corrected HLL estimate
        return E
