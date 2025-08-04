def pack_registers(registers, binbits):
    """
    Packs a list of integer registers into a bytes object using the specified number of bits per register.
    Args:
        registers: List[int] - register values to pack
        binbits: int - number of bits per register
    Returns:
        bytes: packed register data
    """
    m = len(registers)
    bitstream = 0
    for i, val in enumerate(registers):
        bitstream |= (val & ((1 << binbits) - 1)) << (i * binbits)
    needed_bytes = (m * binbits + 7) // 8
    return bitstream.to_bytes(needed_bytes, byteorder='little')

def unpack_registers(data, m, binbits):
    """
    Unpacks a bytes object into a list of integer registers using the specified number of bits per register.
    Args:
        data: bytes - packed register data
        m: int - number of registers
        binbits: int - number of bits per register
    Returns:
        List[int]: unpacked register values
    """
    bitstream = int.from_bytes(data, byteorder='little')
    regs = []
    for i in range(m):
        shift = i * binbits
        val = (bitstream >> shift) & ((1 << binbits) - 1)
        regs.append(val)
    return regs
def compress_sparse_registers(sparse_registers, b, rbits=6):
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
    entrybits = b + rbits
    
    for idx, rho in sparse_registers:
        entry = (idx << rbits) | (rho & ((1 << rbits) - 1))
        bitstream |= entry << total_bits
        total_bits += entrybits

    num_bytes = (total_bits + 7) // 8
    return bitstream.to_bytes(num_bytes, byteorder='little')

def decompress_sparse_registers(data, b, rbits=6):
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
        entry = (bitstream >> shift) & ((1 << entrybits) - 1)
        idx = entry >> rbits
        rho = entry & ((1 << rbits) - 1)
        sparse_registers.append((idx, rho))
    
    return sparse_registers

