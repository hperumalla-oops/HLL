from bisect import bisect_left
import math

from .bias_correction import ALPHA_MM, THRESHOLD, bias_estimate
from .hash_utils import murmurhash64a

class DenseHyperLogLog:
    """
    Dense HyperLogLog implementation (no sparse logic).
    """
    def __init__(self, b=14):
        self.b = b
        self.m = 1 << b
        self.registers = [0] * self.m

    def add(self, item):
        hash_value = murmurhash64a(item)
        idx = hash_value >> (64 - self.b)
        w = (hash_value << self.b) & ((1 << 64) - 1)
        rho = self._rho(w, 64 - self.b)
        self.registers[idx] = max(self.registers[idx], rho)

    def _rho(self, w, max_bits):
        def clzll(x): return 64 - x.bit_length() if x != 0 else 64
        rho = clzll(w) + 1
        if rho == 64:
            while rho < (1 << 6):  # adjust (1 << binbits) for your binbits
                w = murmurhash64a(str(w))
                addn = clzll(w) + 1
                rho += addn
        return rho

    def estimate(self):
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
