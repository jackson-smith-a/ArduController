"""Implement COBS encoding and decoding.

Jackson Smith
Final Project
"""

# basic idea is to replace every zero with the distance to the next zero
# so we can use zeroes as message terminators.

def cobs_decode(in_bytes):
    """Decodes a COBS  encoded byte array.

    Args:
        in_bytes: The COBS encoded byte array to be decoded.

    Returns:
        The decoded byte array.
    """
    
    decoded = bytearray()
    i = 0
    while i < len(in_bytes):
        # beginning will alway be distance to next zero
        next_zero = in_bytes[i]
        i += 1

        j = 1
        # grab bytes until zero
        while j < next_zero and i < len(in_bytes):
            decoded.append(in_bytes[i])
            i += 1
            j += 1

        # patch in zero (unless at an endpoint, then ignore)
        if next_zero != 0xFF and i < len(in_bytes) - 1:
            decoded.append(0)
    return decoded


def cobs_encode(in_bytes):
    """Encodes a byte array into a COBS encoded byte array.

    Args:
        in_bytes: The byte array to be encoded.
        
    Returns:
        The COBS encoded byte array.
    """

    encoded = bytearray(b"\00")

    next_zero = 1
    write_index = 1
    next_zero_index = 0

    i = 0
    while i < len(in_bytes):
        val = in_bytes[i]
        encoded.append(0)

        if val == 0:
            # patch in distance to this zero
            encoded[next_zero_index] = next_zero
            next_zero = 1
            next_zero_index = write_index
            write_index += 1

        else:
            # write in data normally
            encoded[-1] = val
            write_index += 1
            next_zero += 1
            # patch in distance if at an endpoint
            if next_zero == 0xFF:
                encoded[next_zero_index] = next_zero
                next_zero = 1
                next_zero_index = write_index
                write_index += 1

        i += 1

    encoded[next_zero_index] = next_zero
    encoded.append(0)
    return encoded
