from bisect import bisect_left

# ----------------- Bias Correction Tables -----------------
# Copied from Postgres (sample subset for b=14)
ALPHA_MM = {
    14: 0.7213 / (1 + 1.079 / 16384) * (1 << 14)**2
}

THRESHOLD = {14: 5 * (1 << 14)}

rawEstimateData = {
    14: [
        500, 1000, 2000, 5000, 10000, 20000, 50000, 100000
    ]
}

biasData = {
    14: [
        20, 35, 60, 100, 180, 300, 500, 800
    ]
}


def bias_estimate(E, b):
    """Interpolate bias correction for estimate E."""
    raw = rawEstimateData[b]
    bias = biasData[b]
    idx = bisect_left(raw, E)
    if idx == 0:
        return bias[0]
    elif idx == len(raw):
        return bias[-1]
    else:
        # Linear interpolate
        x0, x1 = raw[idx-1], raw[idx]
        y0, y1 = bias[idx-1], bias[idx]
        return y0 + (E - x0) * (y1 - y0) / (x1 - x0)

def clzll(x):
    """Count leading zeros in 64-bit word."""
    return 64 - x.bit_length() if x != 0 else 64
