"""Test COBS encoding algorithms.

Jackson Smith
Final Project
"""

import pytest
from cobs_encoder import cobs_decode, cobs_encode

def test_cobs_encode_distance_greater_than_length():
    input_bytes = bytearray([0x01, 0x02, 0x03, 0xFF, 0x01])
    encoded_bytes = cobs_encode(input_bytes)
    assert encoded_bytes == bytearray(b'\x06\x01\x02\x03\xff\x01\x00')

def test_cobs_encode_distance_greater_than_length_with_zero_padding():
    input_bytes = bytearray([0x01, 0x02, 0x03, 0xFF, 0x01, 0x00])
    encoded_bytes = cobs_encode(input_bytes)
    assert encoded_bytes == bytearray(b'\x06\x01\x02\x03\xff\x01\x01\x00')

def test_cobs_decode_distance_greater_than_length_with_zero_padding():
    input_bytes = bytearray([0x00, 0x01, 0x02, 0x03, 0xFF, 0x01, 0x00])
    decoded_bytes = cobs_decode(input_bytes)
    assert decoded_bytes == bytearray(b'\x00\x00\x03\x00\x01\x00')