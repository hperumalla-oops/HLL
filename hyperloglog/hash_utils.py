

from typing import Union

def murmurhash64a(key: Union[str, bytes], seed: int = 0) -> int:
    """MurmurHash64A ported from C (Postgres)."""
    if isinstance(key, str):
        data = bytearray(key.encode('utf8'))
    elif isinstance(key, bytes):
        data = bytearray(key)
    else:
        raise TypeError("key must be str or bytes")
        
    m = 0xc6a4a7935bd1e995
    r = 47
    length = len(data)
    h = (seed ^ (length * m)) & 0xFFFFFFFFFFFFFFFF

    for i in range(0, length // 8 * 8, 8):
        k = int.from_bytes(data[i:i+8], 'little')
        k = (k * m) & 0xFFFFFFFFFFFFFFFF
        k ^= (k >> r)
        k = (k * m) & 0xFFFFFFFFFFFFFFFF
        h ^= k
        h = (h * m) & 0xFFFFFFFFFFFFFFFF

    remaining = length & 7
    if remaining:
        last_bytes = int.from_bytes(data[-remaining:] + b'\x00'*(8-remaining), 'little')
        h ^= (last_bytes * m) & 0xFFFFFFFFFFFFFFFF
        h = (h * m) & 0xFFFFFFFFFFFFFFFF

    h ^= (h >> r)
    h = (h * m) & 0xFFFFFFFFFFFFFFFF
    h ^= (h >> r)
    return h
