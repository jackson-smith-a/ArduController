"""Handle the program's main GUI.

Jackson Smith
Final Project
"""

import tkinter as tk
import tkinter.filedialog as filedialog
from entry_collection import EntryCollection
from liveplot import LivePlotter
import json

# Default directory for config files
SAVE_DIR = r"/home/nvidia/Documents/ArduController/configs"


def validate_float(value):
    """Validate if the input value is a valid float.

    Args:
        value: The input value to be validated.

    Returns:
        Returns True if the input value is a valid float, otherwise returns False.
    """
    try:
        float(value)
        return True
    except ValueError:
        return value == ""


def validate_pwm(value):
    """Validate if the input value is a valid PWM value.

    Args:
        value: The input value to be validated.

    Returns:
        Returns True if the input value is a valid PWM value, otherwise returns False.
    """
    try:
        return -255 <= int(value) <= 255
    except ValueError:
        return value == ""

# GUI entries
properties = [
    ["General"],
    ["Scaling factor", validate_float, float],
    ["Position"],
    ["Pos KP", validate_float, float],
    ["Pos KI", validate_float, float],
    ["Pos KD", validate_float, float],
    ["Pos min", validate_float, float],
    ["Pos max", validate_float, float],
    ["Pos cutoff", validate_float, float],
    ["Int region", validate_float, float],
    ["Int max", validate_float, float],
    ["Control"],
    ["Target position", validate_float, float],
    ["Analog signal", validate_pwm, int],
]

# default values (blank for now)
defaults = {}


class GUI(tk.Frame):
    """Primary interface for PID tuning."""
    def __init__(self, master, motor_count, ard, setpoint_queue, *args, **kwargs):
        """Initialize the GUI class.

        Args:
            master: The parent Tkinter window.
            motor_count: The number of motors to be controlled.
            ard: The ArduController object that communicates with the hardware.
            setpoint_queue: The queue that holds the setpoint values.
            *args, **kwargs: Additional arguments and keyword arguments for tk.Frame.
        """
        super().__init__(master, *args, **kwargs)

        self.motor_frame = tk.Frame(self)

        self.ard = ard
        self.setpoint_queue = setpoint_queue

        self.motors = []
        for i in range(motor_count):
            motor_entries = EntryCollection(
                self.motor_frame, f"Motor {i}", properties, defaults
            )
            motor_entries.grid(column=i, row=0, padx=15)

            self.motors.append(motor_entries)

        self.motor_frame.grid(column=0, row=0, padx=15, pady=15)

        self.buttons_frame = tk.Frame(self)

        button_commands = [
            ["Send PID", self.send_pid],
            ["Save", self.save],
            ["Load", self.load],
            ["Setpoint", self.update_setpoint],
            ["Reset view", self.reset_view],
            ["Direct set", self.set_motor],
        ]

        self.buttons = {}

        for i, (text, command) in enumerate(button_commands):
            self.buttons[text] = tk.Button(
                self.buttons_frame, text=text, command=command
            )
            self.buttons[text].grid(column=i, row=0, padx=5)

        self.buttons_frame.grid(column=0, row=1, padx=15, pady=15)
        
        self.status = tk.Label(self, text="")
        self.status.grid(column=0, row=2)

        self.plotter = LivePlotter(self, 5, ["Setpoint", "Encoder"], ["black", "red"])
        self.err_plotter = LivePlotter(self, 5, ["Baseline", "Error"], ["black", "red"])
        self.plotter.grid(column=0, row=3)
        self.err_plotter.grid(column=1, row=3)

    def set_motor(self):
        params = self.get()[0]
        self.ard.set_motor(params["Analog signal"])

    def plot(self, encoder, setpoint):
        self.plotter.plot((setpoint, encoder))
        self.err_plotter.plot((0, encoder - setpoint))
        self.err_plotter.reset_view()

    def reset_view(self):
        self.plotter.reset_view()
        self.err_plotter.reset_view()

    def reset_error(self):
        self.err_plotter.reset_view()

    def get(self):
        result = []
        for motor in self.motors:
            params = motor.get()
            for key in params.keys():
                if params[key] is None:
                    params[key] = 0
            result.append(params)
        return result

    def load(self):
        """Load settings from a file"""
        try:
            file = filedialog.askopenfile(mode="r", initialdir=SAVE_DIR)
        except PermissionError:
            self.status["text"] = "Failed to load config. Permission error."
            return
        except FileNotFoundError:
            self.status["text"] = "Failed to load config. File not found."
            return

        try:
            defaults = json.load(file)
            
            for default, motor in zip(defaults, self.motors):
                motor.set(default)
            
            
            self.status["text"] = "Loaded file."

        except ValueError:
            self.status["text"] = "Failed to load config. Invalid JSON."

        file.close()

    def save(self):
        """Save settings to a file"""
        try:
            file = filedialog.asksaveasfile(mode="w", initialdir=SAVE_DIR)
        except PermissionError:
            self.status["text"] = "Failed to save config. Permission error."
            return
        json.dump(self.get(), file)
        file.close()

    def send_pid(self):
        pid_params = self.get()[0]
        self.ard.set_pid(
            KP=pid_params["Pos KP"],
            KI=pid_params["Pos KI"],
            KD=pid_params["Pos KD"],
            zero_output=pid_params["Pos cutoff"],
            min_output=pid_params["Pos min"],
            max_output=pid_params["Pos max"],
            I_region=pid_params["Int region"],
            I_max=pid_params["Int max"],
        )

    def update_setpoint(self):
        params = self.get()[0]
        self.ard.set_position(params["Target position"])
        self.setpoint_queue.put(params["Target position"])
