from cobs_encoder import cobs_encode, cobs_decode
import serial
import time
import struct


class BadCommandError(Exception):
    pass


class Command:
    SET_MOTOR = 1
    REQUEST_ENCODER = 2
    SET_PID = 3
    SET_POSITION = 4


def serial_transaction(method):
    def f(self, *args, **kwargs):
        self._wait_for_unlock()
        if self.closed:
            return
        msg = method(self, *args, **kwargs)
        self._unlock()
        return msg

    return f


class Arduino:
    def __init__(self, port="/dev/ttyACM0", baud_rate=115200):
        self.reopen(port, baud_rate)
    
    def reopen(self, port="/dev/ttyACM0", baud_rate=115200):
        self.ser = serial.Serial(port, baud_rate, timeout=1, write_timeout=1)
        if not self.ser.isOpen():
            self.ser.open()

        time.sleep(3)

        self.locked = False
        self.closed = False

    def _wait_for_unlock(self):
        while self.locked:
            continue
        self.locked = True

    def _unlock(self):
        self.locked = False

    def close(self):
        self.closed = True
        self.ser.close()

    def open(self):
        return self.ser.isOpen()

    def available(self):
        return self.ser.inWaiting()

    def read(self):
        return cobs_decode(self.ser.read_until(b"\00"))

    def write(self, data):
        self.ser.write(cobs_encode(data))
