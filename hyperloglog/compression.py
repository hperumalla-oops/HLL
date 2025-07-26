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
