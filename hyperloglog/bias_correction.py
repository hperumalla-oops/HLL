from .constants import rawEstimateData, biasData

from numpy import searchsorted

def bias_estimate(E: float, b: int) -> float:
    """
    Interpolates the bias correction for a given raw HyperLogLog estimate.

    Args:
        E: float - the raw estimate value for which bias correction is needed.
        b: int - the precision parameter (number of bits) used to index into
                 the precomputed bias and raw estimate tables.

    Returns:
        float: the interpolated bias correction value.
    """
    raw = rawEstimateData[b]     # precomputed raw estimates for precision b
    bias = biasData[b]           # corresponding bias values
    idx = searchsorted(raw, E)   # position of E within the raw estimate array
    if idx == 0:
        return bias[0]
    elif idx == len(raw):
        return bias[-1]
    else:
        # Linear interpolation between (raw[idx-1], bias[idx-1]) and (raw[idx], bias[idx])
        # Equation:
        # bias(E) = bias[idx-1] + (E - raw[idx-1]) * (bias[idx] - bias[idx-1]) / (raw[idx] - raw[idx-1])
        return bias[idx-1] + (E - raw[idx-1]) * (bias[idx] - bias[idx-1]) / (raw[idx] - raw[idx-1])




