from .constants import rawEstimateData, biasData

from numpy import searchsorted

def bias_estimate(E: float, b: int) -> float:
    raw = rawEstimateData[b]
    bias = biasData[b]
    idx = searchsorted(raw, E)
    if idx == 0:
        return bias[0]
    elif idx == len(raw):
        return bias[-1]
    else:
        return bias[idx-1] + (E - raw[idx-1]) * (bias[idx] - bias[idx-1]) / (raw[idx] - raw[idx-1])


