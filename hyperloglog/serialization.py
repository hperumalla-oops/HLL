from hyperloglog import HyperLogLog

def serialize_hll(h: "HyperLogLog") -> str:
    """
    Serialize a HyperLogLog object to a Base64-encoded string.

    This produces a portable string representation of the HLL's
    internal state, suitable for storage or transmission.

    Args:
        h: The HyperLogLog instance to serialize.

    Returns:
        A Base64-encoded string representing the serialized HLL.
    """
    return h.to_base64()


def deserialize_hll(b64_data: str) -> "HyperLogLog":
    """
    Deserialize a Base64-encoded string back into a HyperLogLog object.

    This reverses the `serialize_hll` process and reconstructs
    the HyperLogLog with the same precision, mode, and register data.

    Args:
        b64_data: The Base64-encoded string representation of a HyperLogLog.

    Returns:
        The reconstructed HyperLogLog instance.
    """
    return HyperLogLog.from_base64(b64_data)

