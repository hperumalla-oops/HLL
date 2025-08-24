def pack_registers(registers: list[int], binbits: int) -> bytes:
    """
    Packs a list of integer registers into a bytes object using the specified number of bits per register.
    
    Args:
        registers: List[int] - register values to pack (must be non-negative)
        binbits: int - number of bits per register (must be positive, max 64 for safety)
    
    Returns:
        bytes: packed register data
        
    Raises:
        ValueError: If inputs are invalid
        OverflowError: If the operation would cause memory issues
    """
    # Input validation
    if not isinstance(registers, list):
        raise ValueError("registers must be a list")
    if not isinstance(binbits, int) or binbits <= 0:
        raise ValueError("binbits must be a positive integer")
    if binbits > 64:
        raise ValueError("binbits must be <= 64 to prevent memory issues")
    if not registers:
        return b''
    
    # Check register values
    max_val = (1 << binbits) - 1
    for i, val in enumerate(registers):
        if not isinstance(val, int):
            raise ValueError(f"Register {i} must be an integer")
        if val < 0:
            raise ValueError(f"Register {i} must be non-negative")
        if val > max_val:
            raise ValueError(f"Register {i} value {val} exceeds {binbits}-bit limit ({max_val})")
    
    # Check for potential overflow
    total_bits = len(registers) * binbits
    if total_bits > 2**20:  # Arbitrary safety limit (1MB of bits)
        raise OverflowError(f"Total bits ({total_bits}) too large, risk of memory overflow")
    
    # Pack registers using bitwise operations
    m = len(registers)    # number of registers
    bitstream = 0
    for i, val in enumerate(registers):
        # Equation:
        # bitstream |= (val & ((1 << binbits) - 1)) << (i * binbits)
        # Meaning: take only the lowest 'binbits' bits of val
        # and place them into position (i * binbits) in the bitstream
        bitstream |= (val & ((1 << binbits) - 1)) << (i * binbits)
        
    # Number of bytes = ceil(total bits / 8)
    needed_bytes = (m * binbits + 7) // 8
    return bitstream.to_bytes(needed_bytes, byteorder='little')


def unpack_registers(data: bytes, m: int, binbits: int) -> list[int]:
    """
    Unpacks a bytes object into a list of integer registers using the specified number of bits per register.
    
    Args:
        data: bytes - packed register data
        m: int - number of registers (must be non-negative)
        binbits: int - number of bits per register (must be positive)
    
    Returns:
        List[int]: unpacked register values
        
    Raises:
        ValueError: If inputs are invalid or data is insufficient
    """
    # Input validation
    if not isinstance(data, bytes):
        raise ValueError("data must be bytes")
    if not isinstance(m, int) or m < 0:
        raise ValueError("m must be a non-negative integer")
    if not isinstance(binbits, int) or binbits <= 0:
        raise ValueError("binbits must be a positive integer")
    if binbits > 64:
        raise ValueError("binbits must be <= 64 to prevent memory issues")
    
    if m == 0:
        return []
    
    # Check if we have enough data
    required_bits = m * binbits
    required_bytes = (required_bits + 7) // 8
    if len(data) < required_bytes:
        raise ValueError(f"Insufficient data: need {required_bytes} bytes, got {len(data)}")
    
    # Check for potential overflow
    if required_bits > 2**20:  # Same safety limit as pack
        raise OverflowError(f"Total bits ({required_bits}) too large, risk of memory overflow")
    
    # Unpack registers
    bitstream = int.from_bytes(data, byteorder='little')
    regs = []
    mask = (1 << binbits) - 1    # mask to extract only 'binbits' bits
    
    for i in range(m):
        shift = i * binbits
        # Equation:
        # val = (bitstream >> shift) & mask
        # Meaning: shift down to align, then mask to keep only binbits bits
        val = (bitstream >> shift) & mask
        regs.append(val)
    
    return regs

def compress_sparse_registers(sparse_registers: list[tuple[int, int]], b: int, rbits: int = 6) -> bytes:
    """
    Compresses sparse HLL registers (list of (idx, rho)) into a bytes object.
    Args:
        sparse_registers: List[Tuple[int, int]] - (index, rho) pairs
        b: int - number of bits for the index
        rbits: int - number of bits for rho (default 6)
    Returns:
        bytes: compressed sparse register representation
    """
    bitstream = 0
    total_bits = 0
    entrybits = b + rbits    # total bits per entry
    
    for idx, rho in sparse_registers:
        # Equation:
        # entry = (idx << rbits) | (rho & ((1 << rbits) - 1))
        # Meaning: store idx in higher bits, rho in lower rbits
        entry = (idx << rbits) | (rho & ((1 << rbits) - 1))
        bitstream |= entry << total_bits
        total_bits += entrybits

    # Number of bytes = ceil(total_bits / 8)
    num_bytes = (total_bits + 7) // 8
    return bitstream.to_bytes(num_bytes, byteorder='little')
    
def decompress_sparse_registers(data: bytes, b: int, rbits: int = 6) -> list[tuple[int, int]]:
    """
    Decompresses sparse HLL registers from a bytes object into a list of (idx, rho).
    Args:
        data: bytes - compressed sparse register data
        b: int - number of bits for the index
        rbits: int - number of bits for rho (default 6)
    Returns:
        List[Tuple[int, int]]: decompressed sparse registers
    """
    bitstream = int.from_bytes(data, byteorder='little')
    entrybits = b + rbits
    total_bits = len(data) * 8
    num_entries = total_bits // entrybits

    sparse_registers = []
    for i in range(num_entries):
        shift = i * entrybits
        # Extract entry: (idx in high bits, rho in low rbits)
        entry = (bitstream >> shift) & ((1 << entrybits) - 1)
        idx = entry >> rbits
        rho = entry & ((1 << rbits) - 1)
        sparse_registers.append((idx, rho))
    
    return sparse_registers

