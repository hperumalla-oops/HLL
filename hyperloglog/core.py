from .dense import DenseHyperLogLog
from .sparse import SparseHyperLogLog
from .compression import pack_registers, compress_sparse_registers

class HyperLogLog:
    """
    HyperLogLog (HLL) main interface for cardinality estimation.
    Supports both dense and sparse representations.
    """
    def __init__(self, b=14, mode='sparse', register=0):
        """
        Initializes the HyperLogLog object.

        Args:
            b: int - number of bits used to index registers (precision parameter)
            mode: str - 'dense' or 'sparse' mode
            register: int/bytes - initial register data (0 for empty)
        """
        
        self.b = b # number of bits in the register
        self.mode = mode # dense or sparse 
        self.m = 1 << b
        if mode == 'dense':
            self.impl = DenseHyperLogLog(b, register)
        elif mode == 'sparse':
            self.impl = SparseHyperLogLog(b, register)           
        else:
            raise ValueError('Unknown mode: ' + str(mode))
        self.registers = self.impl.registers

    def add(self, item):
        """
        Adds an item to the HLL structure.
        Args:
            item: any - value to be added (converted to string internally)
        Notes:
            - If adding the item triggers a conversion from sparse to dense mode,
              the internal representation is updated.
        """
        
        if (self.impl.add(str(item))):
            print("Converting to Dense")
            registers = [0] * self.m
            for idx, rho in self.registers:
                registers[idx] = rho
            self.registers = registers
            self.convert_to_dense()

    def estimate(self):
        """
        Returns:
            float: estimated cardinality based on the current HLL state.
        """
        return self.impl.estimate()

    def storing(self):
        """
        Serializes the HLL registers for storage or transmission.

        Returns:
            bytes: packed register data
        """
        if self.mode == 'dense':
            return pack_registers(self.registers, self.b)
        else:
            return compress_sparse_registers(self.registers, self.b )

    def convert_to_dense(self):
        """
        Converts the current HLL from sparse mode to dense mode.
        Updates the internal representation and registers.
        """
        
        self.mode = 'dense'
        self.impl = DenseHyperLogLog(self.b, self.storing())
        self.registers = self.impl.registers

    def merge(self, hll2):
        """
        Merges another HLL object into this one.

        Args:
            hll2: HyperLogLog - another HLL with the same precision parameter b

        Returns:
            float: new estimated cardinality after merging

        Raises:
            ValueError: if the precision parameter (b) values do not match
        """
        
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





