"""Run the main application.

Jackson Smith
Final Project
"""

import tkinter as tk
from gui import GUI

import threading
import time
import queue

from arducontroller import ArduController


def plot_encoders(ard, gui, setpoint_queue):
    """Continuously plots the encoder values and setpoints.

    Args:
        ard (ArduController): The Arduino controller object to retrieve encoder values from.
        gui (GUI): The GUI object to plot the encoder values and setpoints on.
        setpoint_queue (Queue): A queue object to receive setpoints from other parts of the program.
    """
    setpoint = 0
    while True:
        while not setpoint_queue.empty():
            setpoint = setpoint_queue.get()

        if ard.closed:
            break

        enc = ard.request_encoder()[0]
        gui.plot(enc, setpoint)

        time.sleep(0.005)  # 5 ms delay to avoid loading too many datapoints


def on_closing(root, ard):
    """Close GUI and arduino connection."""
    ard.wait_for_unlock()
    ard.close()
    root.destroy()
    root.quit()


def main():
    ard = ArduController()

    setpoint_queue = queue.Queue()

    root = tk.Tk()
    root.title("ArduController")

    gui = GUI(root, 1, ard, setpoint_queue)

    gui.grid(row=0, column=0)

    t1 = threading.Thread(
        target=plot_encoders, args=(ard, gui, setpoint_queue), daemon=True
    )
    t1.start()

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, ard))

    root.mainloop()


main()
