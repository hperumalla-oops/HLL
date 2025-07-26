from .constants import ALPHA_MM, THRESHOLD
import math

def dedupe_and_sort(sparse_data):
    """
    Remove duplicates and sort the sparse data array.
    Returns the deduped count and sorted array.
    """
    unique_data = sorted(set(sparse_data))
    return len(unique_data), unique_data

def hll_estimate_sparse(hloglog_b, hloglog_binbits, sparse_data, sparse_idx):
    """
    Evaluates the stored encoded hashes using linear counting.
    Args:
        hloglog_b: The 'b' parameter (number of index bits)
        hloglog_binbits: Number of bits per bin
        sparse_data: List of encoded hash values
        sparse_idx: Number of elements in sparse_data
    Returns:
        Cardinality estimate using linear counting
    """
    m = 2 ** (32 - 1 - hloglog_binbits)
    sparse_idx, sparse_data_deduped = dedupe_and_sort(sparse_data[:sparse_idx])
    V = 0
    for i in range(sparse_idx):
        if i == 0:
            V += 1
        elif sparse_data_deduped[i] != sparse_data_deduped[i-1]:
            V += 1
    V = sparse_idx
    if m - V <= 0:
        return float('inf')
    estimate = m * math.log(m / (m - V))
    return estimate
