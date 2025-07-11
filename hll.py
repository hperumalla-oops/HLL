import math
from typing import Optional
from helper import hll_get_size_sparse, hll_dense_get_register, pg_decompress, hll_decompress_sparse

class HLLCounter:
    """HyperLogLog Counter data structure"""
    def __init__(self):
        self.version = None
        self.format = None
        self.b = None
        self.binbits = None
        self.idx = None
        self.data = None

# Constants from constants.h
STRUCT_VERSION = 2
MIN_BINBITS = 4
MAX_BINBITS = 8

ERROR_CONST = 1.0816
MIN_INDEX_BITS = 4
MAX_INDEX_BITS = 18


# Format constants
PACKED = 0
PACKED_UNPACKED = 1
UNPACKED = 2
UNPACKED_UNPACKED = 3

def hll_create(ndistinct: float, error: float, format: int) -> HLLCounter:
    """
    Allocate HLL estimator that can handle the desired cardinality and
    precision.
    
    parameters:
        ndistinct   - cardinality the estimator should handle
        error       - requested error rate (0 - 1, where 0 means 'exact')
        format      - storage format (PACKED/UNPACKED)
    
    returns:
        instance of HLL estimator (throws ERROR in case of failure)
    """
    
    #/* target error rate needs to be between 0 and 1 */
    if error <= 0 or error >= 1:
        raise ValueError("invalid error rate requested - only values in (0,1) allowed")
    
    if MIN_BINBITS >= math.ceil(math.log2(math.log2(ndistinct))) or MAX_BINBITS <= math.ceil(math.log2(math.log2(ndistinct))):
        raise ValueError("invalid ndistinct - must be between 257 and 1.1579 * 10^77")

    #/* the counter is allocated as part of this memory block */
    length = hll_get_size_sparse(ndistinct, error)
    p = HLLCounter()

    #/* set the counter struct version */
    p.version = STRUCT_VERSION

    #/* set the format to 0 for bitpacked */
    p.format = format

    #/* what is the minimum number of bins to achieve the requested error rate?
    # *  we'll increase this to the nearest power of two later */
    m = ERROR_CONST / (error * error)

    #/* so how many bits do we need to index the bins (round up to nearest
    # * power of two) */
    p.b = int(math.ceil(math.log2(m)))

    #/* set the number of bits per bin */
    p.binbits = int(math.ceil(math.log2(math.log2(ndistinct))))

    #/* set the starting sparse index to 0 since all counters start sparse and
    # *  empty */
    p.idx = 0

    if p.b < MIN_INDEX_BITS:  #/* we want at least 2^4 (=16) bins */
        p.b = MIN_INDEX_BITS
    elif p.b > MAX_INDEX_BITS:
        raise ValueError(f"number of index bits exceeds MAX_INDEX_BITS (requested {p.b})")

    #/* initialize data array based on sparse size */
    p.data = bytearray(length)

    return p


def hll_unpack(hloglog: HLLCounter) -> HLLCounter:
    """
    Unpacks a packed HLL counter into unpacked format for easier manipulation
    
    parameters:
        hloglog - HLL counter to unpack
        
    returns:
        unpacked HLL counter
    """
    
    if hloglog.format == UNPACKED or hloglog.format == UNPACKED_UNPACKED:
        return hloglog

    #/* use decompress to handle compressed unpacking */
    if hloglog.b < 0:
        return hll_decompress_unpacked(hloglog)

    #/* sparse estimators are unpacked */
    if hloglog.idx != -1:
        return hloglog

    #/* set format to unpacked */
    if hloglog.format == PACKED_UNPACKED:
        hloglog.format = UNPACKED_UNPACKED
    elif hloglog.format == PACKED:
        hloglog.format = UNPACKED

    #/* allocate and zero an array large enough to hold all the decompressed
    #* bins */
    m = 2 ** hloglog.b  #/* POW2(hloglog->b) */
    htemp = HLLCounter()
    
    #/* copy header data */
    htemp.version = hloglog.version
    htemp.format = hloglog.format
    htemp.b = hloglog.b
    htemp.binbits = hloglog.binbits
    htemp.idx = hloglog.idx

    #/* allocate new data array */
    htemp.data = bytearray(m)

    for i in range(m):
        #/* HLL_DENSE_GET_REGISTER equivalent */
        entry = hll_dense_get_register(hloglog.data, i, hloglog.binbits)
        htemp.data[i] = entry

    return htemp


def hll_decompress_unpacked(hloglog: HLLCounter) -> HLLCounter:
    """
    Decompresses a compressed HLL counter into unpacked format
    
    parameters:
        hloglog - compressed HLL counter
        
    returns:
        decompressed unpacked HLL counter
    """
    
    #/* make sure the data is compressed */
    if hloglog.b > 0:
        return hloglog

    if hloglog.idx == -1:
        hloglog = hll_decompress_dense_unpacked(hloglog)
    else:
        hloglog = hll_decompress_sparse(hloglog)

    return hloglog


def hll_decompress_dense_unpacked(hloglog: HLLCounter) -> HLLCounter:
    """
    Decompresses dense counters from compressed format
    
    parameters:
        hloglog - compressed dense HLL counter
        
    returns:
        decompressed dense HLL counter
    """
    
    #/* reset b to positive value for calcs and to indicate data is
    #* decompressed */
    hloglog.b = -1 * hloglog.b
    hloglog.format = UNPACKED

    #/* allocate and zero an array large enough to hold all the decompressed
    #* bins */
    m = 2 ** hloglog.b  #/* POW2(hloglog->b) */
    htemp = HLLCounter()
    
    #/* copy header information */
    htemp.version = hloglog.version
    htemp.format = hloglog.format
    htemp.b = hloglog.b
    htemp.binbits = hloglog.binbits
    htemp.idx = hloglog.idx
    
    #/* allocate new data array */
    htemp.data = bytearray(m)

    #/* decompress the data */
    #/* pg_decompress equivalent - would need custom decompression implementation */
    decompressed_data = pg_decompress(hloglog.data)
    htemp.data[:len(decompressed_data)] = decompressed_data

    return htemp

