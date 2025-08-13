from .dense import DenseHyperLogLog
from .sparse import SparseHyperLogLog
from .compression import pack_registers, compress_sparse_registers

class HyperLogLog:
    """
    HyperLogLog (HLL) main interface for cardinality estimation.
    Supports both dense and sparse representations.
    """
    def __init__(self, b: int = 14, mode: str = 'sparse', register: int | bytes = 0):
        """
        Initializes the HyperLogLog object.

        Args:
            b: int - number of bits used to index registers (precision parameter)
            mode: str - 'dense' or 'sparse' mode
            register: int/bytes - initial register data (0 for empty)
        """
        if b in range(4,19):
            self.b = b # number of bits in the register
        else:
             raise ValueError("Value of b not in range [4,18]")
            
        self.mode = mode # dense or sparse 
        self.m = 1 << b
        if mode == 'dense':
            self.impl = DenseHyperLogLog(b, register)
        elif mode == 'sparse':
            self.impl = SparseHyperLogLog(b, register)           
        else:
            raise ValueError('Unknown mode: ' + str(mode))
        self.registers = self.impl.registers

    def add(self, item: object ) -> None :
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
            self.convert_to_dense()

    def estimate(self) -> float:
        """
        Returns:
            float: estimated cardinality based on the current HLL state.
        """
        return self.impl.estimate()

    def storing(self) -> bytes:
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

        if self.mode == 'sparse':
            # Convert sparse representation (list of (idx, rho)) to dense list of ints
            registers = [0] * self.m
            for idx, rho in self.registers:
                registers[idx] = rho
            self.registers = registers  # now dense list

        self.mode = 'dense'
        self.impl = DenseHyperLogLog(self.b, self.storing())
        self.registers = self.impl.registers


    def merge(self, hll2):
         """
        Merges another HLL object into this one, matching C implementation logic.
    
        Args:
            hll2: HyperLogLog - another HLL with the same precision parameter b
    
        Returns:
            HLL object: the currect HLL object with hll2's registers.
    
        Raises:
            ValueError: if the precision parameter (b) values do not match
        """
        
        if self.b != hll2.b:
            raise ValueError("Cannot merge HLLs with different precision (b) values")

        m = 1 << self.b

        if self.mode == 'dense' and hll2.mode == 'dense':
            self.impl.registers = [
                max(self.impl.registers[i], hll2.impl.registers[i]) for i in range(m)
            ]
            return self

        if self.mode == 'dense' and hll2.mode == 'sparse':
            for idx, rho in hll2.registers:
                if rho > self.impl.registers[idx]:
                    self.impl.registers[idx] = rho
            return self

        if self.mode == 'sparse' and hll2.mode == 'dense':
            self.convert_to_dense()
            for i in range(m):
                self.impl.registers[i] = max(
                    self.impl.registers[i], hll2.impl.registers[i]
                )
            return self

        if self.mode == 'sparse' and hll2.mode == 'sparse':
            self_sparse = list(self.registers)
            other_sparse = list(hll2.registers)
            self_sparse.extend(other_sparse)

            deduped = {}
            for idx, rho in self_sparse:
                if idx not in deduped or rho > deduped[idx]:
                    deduped[idx] = rho

            self.registers = sorted(deduped.items())

            if len(self.registers) > (m * (7.0 / 8)):
                self.convert_to_dense()
                return self.merge(hll2)

            return self



    
    








