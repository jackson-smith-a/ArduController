"""Pack and unpack Python objects to and from bytes.

Jackson Smith
Final Project
"""


import struct

def pack_values(args, message=b""):
    """
    Pack a list of values into a binary message.

    Args:
        args: A list of values to be packed.
        message: A binary message to which the values will be appended. Defaults to b"".

    Returns:
        A binary message containing the packed values.
    """
    if len(args) == 0:
        return message

    arg, *rest = args
    
    # pack known datatypes
    if isinstance(arg, int):
        message += struct.pack("i", arg)
    elif isinstance(arg, float):
        message += struct.pack("f", arg)
    elif isinstance(arg, bytes) or isinstance(arg, bytearray):
        message += arg
    else:
        raise ValueError(f"Can't pack value of datatype {type(arg)}")
        
    return pack_values(rest, message)

def unpack_values(msg, pattern, results=None):
    """
    Unpack a binary message into a list of values.

    Args:
        msg: A binary message to be unpacked.
        pattern: A string representing the format of the binary message.
        results: A list to store the unpacked values. Defaults to None.

    Returns:
        A tuple containing the list of unpacked values and the remaining bytes in the message.
    """
    if results == None:
        results = []
        
    if len(pattern) == 0:
        return results, msg

    char, *pattern = pattern

    # grab first 4 bytes
    value = msg[:4]
    msg = msg[4:]
    if char == "i":
        results.append(struct.unpack("i", value)[0])
    elif char == "f":
        results.append(struct.unpack("f", value)[0])

    return unpack_values(msg, pattern, results)
    
