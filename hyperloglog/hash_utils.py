from typing import Union

def murmurhash64a(key: Union[str, bytes], seed: int = 0) -> int:
    """
    MurmurHash64A implementation ported from C (PostgreSQL).
    
    Args:
        key: The data to hash. Can be either a string (UTF-8 encoded) or bytes.
        seed: Initial seed value for the hash function. Defaults to 0.
              Different seeds produce different hash values for the same input.
    
    Returns:
        A 64-bit integer hash value.
        
    Raises:
        TypeError: If key is neither str nor bytes.

    """
    # Convert input to bytearray for consistent processing
    if isinstance(key, str):
        byte_data = bytearray(key.encode('utf8'))
    elif isinstance(key, bytes):
        byte_data = bytearray(key)
    else:
        raise TypeError("key must be str or bytes")
    
    # MurmurHash64A constants
    MULTIPLIER = 0xc6a4a7935bd1e995  # Large prime multiplier for mixing
    RIGHT_SHIFT = 47                  # Bit shift amount for avalanche effect
    MASK_64BIT = 0xFFFFFFFFFFFFFFFF   # Mask to keep values within 64-bit range
    
    data_length = len(byte_data)
    
    # Initialize hash with seed and data length
    hash_value = (seed ^ (data_length * MULTIPLIER)) & MASK_64BIT
    
    # Process data in 8-byte (64-bit) chunks
    bytes_per_chunk = 8
    full_chunks_end = (data_length // bytes_per_chunk) * bytes_per_chunk
    
    for chunk_start in range(0, full_chunks_end, bytes_per_chunk):
        # Extract 8 bytes as little-endian 64-bit integer
        chunk_bytes = byte_data[chunk_start:chunk_start + bytes_per_chunk]
        chunk_value = int.from_bytes(chunk_bytes, 'little')
        
        # Mix the chunk value
        chunk_value = (chunk_value * MULTIPLIER) & MASK_64BIT
        chunk_value ^= (chunk_value >> RIGHT_SHIFT)
        chunk_value = (chunk_value * MULTIPLIER) & MASK_64BIT
        
        # Combine with running hash
        hash_value ^= chunk_value
        hash_value = (hash_value * MULTIPLIER) & MASK_64BIT
    
    # Handle remaining bytes (less than 8 bytes)
    remaining_byte_count = data_length & 7  # Equivalent to data_length % 8
    
    if remaining_byte_count:
        # Pad remaining bytes to 8 bytes with zeros on the right
        remaining_bytes = byte_data[-remaining_byte_count:]
        padding_needed = bytes_per_chunk - remaining_byte_count
        padded_bytes = remaining_bytes + b'\x00' * padding_needed
        
        # Process the padded final chunk
        final_chunk_value = int.from_bytes(padded_bytes, 'little')
        hash_value ^= (final_chunk_value * MULTIPLIER) & MASK_64BIT
        hash_value = (hash_value * MULTIPLIER) & MASK_64BIT
    
    # Final mixing (avalanche effect)
    hash_value ^= (hash_value >> RIGHT_SHIFT)
    hash_value = (hash_value * MULTIPLIER) & MASK_64BIT
    hash_value ^= (hash_value >> RIGHT_SHIFT)
    
    return hash_value

