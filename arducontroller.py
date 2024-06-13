"""Communicate to an Arduino running ArduController firmware.

Jackson Smith
Final Project
"""


from arduino import Arduino, serial_transaction
from byte_packing import pack_values, unpack_values


class BadCommandError(Exception):
    """Exception raised when passing an invalid command to Arduino."""
    pass


class Command:
    """Command IDs that Arduino understands.s"""
    SET_MOTOR = 1
    REQUEST_ENCODER = 2
    SET_PID = 3
    SET_POSITION = 4



class ArduController(Arduino):
    """Handles communication between Arduino and Jetson."""
    def __init__(self, port="/dev/ttyACM0", baud_rate=115200):
        """
        Initializes the Arduino object with the specified serial port and baud rate.

        Args:
            port (str): The serial port to connect to. Default is "/dev/ttyACM0".
            baud_rate (int): The baud rate for the serial connection. Default is 115200.
        """
        super().__init__(port, baud_rate)

    @serial_transaction
    def set_motor(self, speed):
        """Set the motor speed.

        Args:
            speed: between -255 and 255, inclusive.
        """
        assert -255 <= speed <= 255
        self.send_command(Command.SET_MOTOR, (int(speed),))

    @serial_transaction
    def set_pid(self, KP, KI, KD, zero_output, min_output, max_output, I_region, I_max):
        """Set the PID parameters.

        Args:
            KP: Proportional gain.
            KI: Integral gain.
            KD: Derivative gain.
            zero_output: Output cutoff.
            min_output: Minimum output.
            max_output: Maximum output.
            I_region: Integration region.
            I_max: Integration max.
        """
        self.send_command(Command.SET_PID,
            (float(KP),
            float(KI),
            float(KD),
            float(zero_output),
            float(min_output),
            float(max_output),
            float(I_region),
            float(I_max))
        )

    @serial_transaction
    def set_position(self, position):
        """Set PID setpoint.

        Args:
            position: new setpoint

        Returns:
            echoed back position for confirmation
        """
        self.send_command(Command.SET_POSITION, (int(position),))
        reply = self.read_pattern("i")[0]
        return reply

    @serial_transaction
    def request_encoder(self):
        """Request encoder counts from arduino.

        Returns:
            List of all encoders positions.
        """
        self.send_command(Command.REQUEST_ENCODER)
        results, msg = self.read_pattern("i")
        return results

    
    def send_command(self, command, args=()):
        """Send a command to the Arduino.

        Args:
            command: Instruction ID from Command
            args: values to send
        """
        message = bytes([command])
        try:
            message += pack_values(args)
            self.write(message)
        except ValueError:
            raise BadCommandError(f"Invalid command argument list {repr(args)}")

    def read_pattern(self, pattern):
        """Read values from the Arduino given a pattern.

        Args:
            pattern: string. each "f" indicates a float, each "i" an integer.
            
        Example usage:
            ard.read_pattern("fif")
        Will read and return a float, then an integer, then a float.

        Returns:
            list of read values.
        """
        msg = self.read()
        results, msg = unpack_values(msg, pattern)
        return results, msg
