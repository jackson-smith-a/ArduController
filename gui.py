import tkinter as tk
import tkinter.filedialog as filedialog
from entry_collection import EntryCollection
from liveplot import LivePlotter
import pickle


SAVE_DIR = r"/home/nvidia/Documents/ArduController/configs"

def validate_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return value == ""


def validate_pwm(value):
    try:
        return -255 <= int(value) <= 255
    except ValueError:
        return value == ""


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
    ["Analog signal", validate_pwm, int]
]

defaults = {}


class GUI(tk.Frame):
    def __init__(self, master, motors, ard, setpoint_queue, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.motor_frame = tk.Frame(self)
        
        self.ard = ard
        self.setpoint_queue = setpoint_queue

        self.motors = []
        for i in range(motors):
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
            ["Direct set", self.set_motor]
        ]
        
        self.buttons = {}

        for i, (text, command) in enumerate(button_commands):
            self.buttons[text] = tk.Button(self.buttons_frame, text=text, command=command)
            self.buttons[text].grid(column=i, row=0, padx=5)

        self.buttons_frame.grid(column=0, row=1, padx=15, pady=15)
        
        self.plotter = LivePlotter(self, 5, ["Setpoint", "Encoder"], ["black", "red"])
        self.err_plotter = LivePlotter(self, 5, ["Baseline", "Error"], ["black", "red"])
        self.plotter.grid(column=0, row=2)
        self.err_plotter.grid(column=1, row=2)
     
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
        file = filedialog.askopenfile(mode="rb", initialdir=SAVE_DIR)
        defaults = pickle.load(file)
        file.close()
        for default, motor in zip(defaults, self.motors):
            motor.set(default)
            

    def save(self):
        """Save settings to a file"""
        file = filedialog.asksaveasfile(mode="wb", initialdir=SAVE_DIR)
        pickle.dump(self.get(), file)
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
          I_max=pid_params["Int max"]
        )
    
    def update_setpoint(self):
        params = self.get()[0]
        self.ard.set_position(params["Target position"])
        self.setpoint_queue.put(params["Target position"])
