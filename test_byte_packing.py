"""Test byte packing.

Jackson Smith
Final Project
"""

import pytest
from byte_packing import pack_values, unpack_values

def test_pack_values():
    # Arrange
    input_values = [1, 2.5, 2]

    # Act
    packed_message = pack_values(input_values)

    assert packed_message == b'\x01\x00\x00\x00\x00\x00 @\x02\x00\x00\x00'
    
def test_unpack_values():
    # Arrange
    input_values = b'\x01\x00\x00\x00\x00\x00 @\x02\x00\x00\x00'

    # Act
    packed_message, msg = unpack_values(input_values, "ifi")

    assert packed_message == [1, 2.5, 2]
    assert msg == b""
