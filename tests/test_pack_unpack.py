import unittest
from typing import List
from hyperloglog.compression import unpack_registers, pack_registers

class TestRegisterPackingIntegration(unittest.TestCase):
    """Integration tests for more complex scenarios."""

    def test_various_bit_widths_systematic(self):
        """Systematically test all bit widths from 1 to 16."""
        for binbits in range(1, 17):
            max_val = (1 << binbits) - 1
            
            # Test with various patterns
            test_patterns = [
                [0],
                [max_val],
                [0, max_val],
                [max_val, 0],
                list(range(min(8, max_val + 1))),  # Sequential values
            ]
            
            for pattern in test_patterns:
                if all(v <= max_val for v in pattern):
                    with self.subTest(binbits=binbits, pattern=pattern):
                        packed = pack_registers(pattern, binbits)
                        unpacked = unpack_registers(packed, len(pattern), binbits)
                        self.assertEqual(unpacked, pattern)

    def test_stress_random_data(self):
        """Stress test with pseudo-random data."""
        import random
        random.seed(42)  # Reproducible
        
        for _ in range(100):
            binbits = random.randint(1, 16)
            max_val = (1 << binbits) - 1
            count = random.randint(1, 50)
            
            registers = [random.randint(0, max_val) for _ in range(count)]
            
            packed = pack_registers(registers, binbits)
            unpacked = unpack_registers(packed, len(registers), binbits)
            self.assertEqual(unpacked, registers)

    # Test the overflow protection logic
def test_overflow():
    # Test what actually triggers overflow
    limit = 2**20  # 1,048,576 bits
    
    print(f"Limit: {limit} bits")
    print(f"For 8-bit registers: {limit // 8} = {limit // 8} registers exactly")
    print(f"Need {(limit // 8) + 1} registers to exceed limit")
    
    # Test edge cases
    exactly_at_limit = limit // 8  # 131,072 registers
    over_limit = exactly_at_limit + 1  # 131,073 registers
    
    print(f"\nTesting {exactly_at_limit} registers * 8 bits = {exactly_at_limit * 8} bits")
    print(f"Should this trigger overflow? {exactly_at_limit * 8 > limit}")
    
    print(f"\nTesting {over_limit} registers * 8 bits = {over_limit * 8} bits") 
    print(f"Should this trigger overflow? {over_limit * 8 > limit}")
    
    # Actually test with the functions
    try:
        result = pack_registers([1] * exactly_at_limit, 8)
        print(f"✓ {exactly_at_limit} registers worked (no overflow)")
    except OverflowError as e:
        print(f"✗ {exactly_at_limit} registers failed: {e}")
    
    try:
        result = pack_registers([1] * over_limit, 8)
        print(f"✗ {over_limit} registers worked (should have failed!)")
    except OverflowError as e:
        print(f"✓ {over_limit} registers failed as expected: {e}")

if __name__ == "__main__":
    test_overflow()

# if __name__ == '__main__':
#     # Run with verbose output
#     unittest.main(verbosity=2)