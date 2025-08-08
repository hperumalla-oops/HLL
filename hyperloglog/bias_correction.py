from bisect import bisect_left
from .constants import rawEstimateData, biasData

def bias_estimate(E, b):
    """
    Interpolates the bias correction for a given estimate value.
    Args:
        E: float - the raw estimate value for which bias correction is needed
        b: int - index into precomputed bias and raw estimate tables
    Returns:
        float: the interpolated bias correction value
    """
    raw = rawEstimateData[b]
    bias = biasData[b]
    idx = bisect_left(raw, E)
    if idx == 0:
        return bias[0]
    elif idx == len(raw):
        return bias[-1]
    else:
        x0, x1 = raw[idx-1], raw[idx]
        y0, y1 = bias[idx-1], bias[idx]
        return y0 + (E - x0) * (y1 - y0) / (x1 - x0)

