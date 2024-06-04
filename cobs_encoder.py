def cobs_decode(in_bytes):
    decoded = bytearray()
    i = 0
    while i < len(in_bytes):
        next_zero = in_bytes[i]
        i += 1

        j = 1
        while j < next_zero and i < len(in_bytes):
            decoded.append(in_bytes[i])
            i += 1
            j += 1

        if next_zero != 0xFF and i < len(in_bytes) - 1:
            decoded.append(0)
    return decoded


def cobs_encode(in_bytes):
    encoded = bytearray(b"\00")

    next_zero = 1
    write_index = 1
    next_zero_index = 0

    i = 0
    while i < len(in_bytes):
        val = in_bytes[i]
        encoded.append(0)

        if val == 0:
            encoded[next_zero_index] = next_zero
            next_zero = 1
            next_zero_index = write_index
            write_index += 1

        else:
            encoded[-1] = val
            write_index += 1
            next_zero += 1
            if next_zero == 0xFF:
                encoded[next_zero_index] = next_zero
                next_zero = 1
                next_zero_index = write_index
                write_index += 1

        i += 1

    encoded[next_zero_index] = next_zero
    encoded.append(0)
    return encoded
