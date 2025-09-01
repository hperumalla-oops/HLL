from .dense import DenseHyperLogLog
from .sparse import SparseHyperLogLog
from .compression import pack_registers, compress_sparse_registers
import base64
import struct

class HyperLogLog:
    """
    HyperLogLog (HLL) main interface, delegating to sparse or dense implementations.
    """
    def __init__(self, b: int = 14, mode: str = 'sparse', register: int | bytes = 0):
        """Initializes the HyperLogLog object."""
        if not isinstance(b, int) or not (4 <= b <= 18):
            raise ValueError("Value of b not in range [4,18]")
        
        if not isinstance(b, int) or not (4 <= b <= 18):
            raise ValueError("Value of b not in range [4,18]")
        else:
            self.b=b
            
        self.mode = mode.lower()
        self.m = 1 << b
        
        if self.mode == 'dense':
            self.impl = DenseHyperLogLog(b, register)
        elif self.mode == 'sparse':
            self.impl = SparseHyperLogLog(b, register)
        else:
            raise ValueError("Mode must be 'sparse' or 'dense'")
        # CORRECTED: The stale self.registers reference has been removed.

    def add(self, item: object) -> None:
        """Adds an item to the HLL, converting to dense mode if necessary."""
        if self.impl.add(str(item)):
            # Signal received from sparse impl to convert to dense
            self.convert_to_dense()

    def estimate(self) -> float:
        """Returns the estimated cardinality."""
        return self.impl.estimate()

    def storing(self) -> bytes:
        """Serializes the HLL registers for storage."""
        if self.mode == 'dense':
            # CORRECTED: Use 6 bits for packing dense registers and access via self.impl
            return pack_registers(self.impl.registers, 6)
        else:
            # CORRECTED: Access registers via self.impl
            return compress_sparse_registers(self.impl.registers, self.b)

    def convert_to_dense(self):
        """Converts the HLL from sparse to dense mode."""
        if self.mode == 'sparse':
            sparse_regs = self.impl.registers
            dense_registers = [0] * self.m
            for idx, rho in sparse_regs.items():
                dense_registers[idx] = rho

            # CORRECTED: Use 6 bits for packing dense registers
            packed = pack_registers(dense_registers, 6)

            self.mode = 'dense'
            self.impl = DenseHyperLogLog(self.b, packed)

    def merge(self, hll2: "HyperLogLog"):
        """Merges another HLL object into this one."""
        if self.b != hll2.b:
            raise ValueError("Cannot merge HLLs with different precision")

        # Case 1: both dense
        if self.mode == 'dense' and hll2.mode == 'dense':
            for i in range(self.m):
                self.impl.registers[i] = max(self.impl.registers[i], hll2.impl.registers[i])
            return self

        # Case 2: self dense, other sparse
        if self.mode == 'dense' and hll2.mode == 'sparse':
            # CORRECTED: Access registers via self.impl
            for idx, rho in hll2.impl.registers.items():
                if rho > self.impl.registers[idx]:
                    self.impl.registers[idx] = rho
            return self

        # Case 3: self sparse, other dense
        if self.mode == 'sparse' and hll2.mode == 'dense':
            self.convert_to_dense()
            # CORRECTED: Cleaner logic to re-run merge after conversion
            return self.merge(hll2) 

        # Case 4: both sparse
        if self.mode == 'sparse' and hll2.mode == 'sparse':
            # CORRECTED: Access registers via self.impl
            for idx, rho in hll2.impl.registers.items():
                current_rho = self.impl.registers.get(idx, 0)
                if rho > current_rho:
                    self.impl.registers[idx] = rho
            
            # After merge, check if it's full enough to convert
            if len(self.impl.registers) > self.impl.sparse_threshold:
                self.convert_to_dense()
            return self

    def to_bytes(self) -> bytes:
        """Serializes the HLL into a stable, self-describing binary format."""
        magic = b"HLL1"
        mode_flag = 0 if self.mode == "dense" else 1
        payload = self.storing()
        header = magic + bytes([self.b, mode_flag]) + struct.pack(">I", len(payload))
        return header + payload

    @classmethod
    def from_bytes(cls, blob: bytes) -> "HyperLogLog":
        """Reconstructs an HLL from its binary format."""
        if len(blob) < 10:
            raise ValueError("HLL blob too short")
            
        magic, b_val, mode_flag = blob[:4], blob[4], blob[5]
        if magic != b"HLL1":
            raise ValueError("Invalid HLL magic/version")
            
        mode = "dense" if mode_flag == 0 else "sparse"
        (length,) = struct.unpack(">I", blob[6:10])
        
        if len(blob) != 10 + length:
            raise ValueError("Invalid HLL payload length")
            
        payload = blob[10:]
        return cls(b=b_val, mode=mode, register=payload)

    def to_base64(self) -> str:
        """Returns a Base64 representation of the serialized HLL."""
        return base64.b64encode(self.to_bytes()).decode("ascii")

    @classmethod
    def from_base64(cls, s: str) -> "HyperLogLog":
        """Builds an HLL from a Base64 string."""
        data = base64.b64decode(s)
        return cls.from_bytes(data)
