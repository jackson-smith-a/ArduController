from arduino import Arduino, serial_transaction
from byte_packing import pack_values, unpack_values
import struct


class BadCommandError(Exception):
    pass


class Command:
    SET_MOTOR = 1
    REQUEST_ENCODER = 2
    SET_PID = 3
    SET_POSITION = 4



class ArduController(Arduino):
    def __init__(self, port="/dev/ttyACM0", baud_rate=115200):
        super().__init__(port, baud_rate)

    @serial_transaction
    def set_motor(self, speed):
        self.send_command(Command.SET_MOTOR, (int(speed),))

    @serial_transaction
    def set_pid(self, KP, KI, KD, zero_output, min_output, max_output, I_region, I_max):
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
        self.send_command(Command.SET_POSITION, (int(position),))
        reply = self.read_pattern("i")[0]
        return reply

    @serial_transaction
    def request_encoder(self):
        self.send_command(Command.REQUEST_ENCODER)
        results, msg = self.read_pattern("i")
        return results

    
    def send_command(self, instruction, args=()):
        message = bytes([instruction])
        try:
            message += pack_values(args)
        except ValueError:
            raise BadCommandError(f"Invalid command argument list {repr(args)}")
        self.write(message)

    def read_pattern(self, pattern):
        msg = self.read()
        results, msg = unpack_values(msg, pattern)
        return results, msg
