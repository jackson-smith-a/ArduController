from arduino import Arduino, serial_transaction
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
        self.send_command(Command.SET_MOTOR, int(speed))

    @serial_transaction
    def set_pid(self, KP, KI, KD, zero_output, min_output, max_output, I_region, I_max):
        self.send_command(
            Command.SET_PID,
            float(KP),
            float(KI),
            float(KD),
            float(zero_output),
            float(min_output),
            float(max_output),
            float(I_region),
            float(I_max),
        )

    @serial_transaction
    def set_position(self, position):
        self.send_command(Command.SET_POSITION, int(position))
        reply = self.read_pattern("i")[0]
        return reply

    @serial_transaction
    def request_encoder(self):
        self.send_command(Command.REQUEST_ENCODER)
        results, msg = self.read_pattern("i")
        return results

    
    def send_command(self, instruction, *args):
        message = bytes([instruction])
        for arg in args:
            if isinstance(arg, int):
                message += struct.pack("i", arg)
            elif isinstance(arg, float):
                message += struct.pack("f", arg)
            elif isinstance(arg, bytes) or isinstance(arg, bytearray):
                message += arg
            else:
                raise BadCommandError(f"Cannot send commands of datatype {type(arg)}")
        self.write(message)

    def read_pattern(self, pattern):
        msg = self.read()
        results = []
        for char in pattern:
            value = msg[:4]
            msg = msg[4:]
            if char == "i":
                results.append(struct.unpack("i", value)[0])
            elif char == "f":
                results.append(struct.unpack("@f", value)[0])
        return results, msg
