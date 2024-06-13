import struct

def pack_values(args):
    message = b""
    for arg in args:
        if isinstance(arg, int):
            message += struct.pack("i", arg)
        elif isinstance(arg, float):
            message += struct.pack("f", arg)
        elif isinstance(arg, bytes) or isinstance(arg, bytearray):
            message += arg
        else:
            raise ValueError(f"Can't pack value of datatype {type(arg)}")
    return message

def unpack_values(msg, pattern):
    results = []
    for char in pattern:
        value = msg[:4]
        msg = msg[4:]
        if char == "i":
            results.append(struct.unpack("i", value)[0])
        elif char == "f":
            results.append(struct.unpack("f", value)[0])
    return results, msg

