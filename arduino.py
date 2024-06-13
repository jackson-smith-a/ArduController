"""Communicate with any Arduino using COBS encoding.

Jackson Smith
Final Project
"""


from cobs_encoder import cobs_encode, cobs_decode
import serial
import time

def serial_transaction(method):
    """
    Decorator for thread-safe serial communication.

    Args:
        method: The method to be executed in the serial transaction.

    Returns:
        The decorated function that executes the serial transaction.
    """
    def f(self, *args, **kwargs):
        # let current transaction finish
        self.wait_for_unlock()
        
        # make sure Arduino is open
        if self.closed:
            return
        
        # call method
        msg = method(self, *args, **kwargs)
        
        # unlock it for next transaction
        self.unlock()
        return msg

    return f


class Arduino:
    """An interface for Arduino communication through COBS encoding."""
    def __init__(self, port="/dev/ttyACM0", baud_rate=115200):
        """
        Initializes the Arduino object with the specified serial port and baud rate.

        Args:
            port (str): The serial port to connect to. Default is "/dev/ttyACM0".
            baud_rate (int): The baud rate for the serial connection. Default is 115200.
        """
        self.reopen(port, baud_rate)
    
    def reopen(self, port="/dev/ttyACM0", baud_rate=115200):
        """
        Reopens the serial connection with the specified serial port and baud rate.

        Args:
            port (str): The serial port to connect to. Default is "/dev/ttyACM0".
            baud_rate (int): The baud rate for the serial connection. Default is 115200.
        """
        self.ser = serial.Serial(port, baud_rate, timeout=1, write_timeout=1)
        if not self.ser.isOpen():
            self.ser.open()

        time.sleep(3)

        self.locked = False
        self.closed = False

    def wait_for_unlock(self):
        """Wait until the serial port is unlocked, then relock it.s"""
        while self.locked:
            continue
        self.locked = True

    def unlock(self):
        """Unlock the serial port."""
        self.locked = False

    def close(self):
        """Close the serial port."""
        self.closed = True
        self.ser.close()

    def open(self):
        """Check if the serial port is open.

        Returns:
            True if the port is open, False otherwise.
        """
        return self.ser.isOpen()

    def available(self):
        """Check if the serial port is available.
        
        Returns:
            True if the port is available, False otherwise.
        """
        return self.ser.inWaiting()

    def read(self):
        """Read a COBS packet from the serial port.

        Returns:
            Read bytes.
        """
        if self.closed:
            return None
        return cobs_decode(self.ser.read_until(b"\00"))

    def write(self, data):
        """Write a COBS packet to the serial port.

        Args:
            data: data to be written to the serial port.
        """
        self.ser.write(cobs_encode(data))
