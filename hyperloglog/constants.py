# Alpha * m^2 for each b (Postgres/Flajolet values)
ALPHA_MM = {
    14: 0.7213 / (1 + 1.079 / 16384) * (1 << 14) ** 2
    # Add more b values as needed
}

# Thresholds for switching between bias-corrected and linear counting
THRESHOLD = {
    14: 5 * (1 << 14)
    # Add more b values as needed
}

# Raw estimate and bias data for bias correction (example for b=14)
rawEstimateData = {
    14: [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    # Add more b values as needed
}

biasData = {
    14: [20, 35, 60, 100, 180, 300, 500, 800]
    # Add more b values as needed
}
