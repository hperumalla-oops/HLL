import mmh3
from typing import Union

def murmurhash64a(key: Union[str, bytes], seed: int = 0) -> int:
    """
    MurmurHash64A using mmh3 instead of manual implementation.
    
    Args:
        key: Data to hash (string or bytes).
        seed: Initial seed value for the hash function. Defaults to 0.
    
    Returns:
        A 64-bit integer hash value (unsigned).
    
    Raises:
        TypeError: If key is neither str nor bytes.
    """
    if isinstance(key, str):
        key_bytes = key.encode("utf8")
    elif isinstance(key, bytes):
        key_bytes = key
    else:
        raise TypeError("key must be str or bytes")

    # mmh3.hash64 returns a tuple (low64, high64)
    low64, high64 = mmh3.hash64(key_bytes, seed=seed, signed=False)


    # we return the low 64-bit value (just like PostgreSQL does).
    return low64

