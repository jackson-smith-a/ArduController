import tkinter as tk
from gui import GUI

import random
import threading
import time
import queue

from arduino import Arduino

def plot_encoders(ard, gui, setpoint_queue):
	setpoint = 0
	while not ard.closed:
		while not setpoint_queue.empty():
			setpoint = setpoint_queue.get()

		enc = ard.request_encoder()[0]
		gui.plot(enc, setpoint)

		time.sleep(0.005) # 5 ms delay to avoid loading too many datapoints


def on_closing(root, ard, t1):
	ard.close()
	root.quit()
	root.destroy()

	
def main():
	ard = Arduino()
	
	setpoint_queue = queue.Queue()
	
	root = tk.Tk()

	gui = GUI(root, 1, ard, setpoint_queue)

	gui.grid(row=0, column=0)
	
	
	t1 = threading.Thread(target=plot_encoders, args=(ard, gui, setpoint_queue), daemon=True)
	t1.start()
	
	
	root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, ard, t1))


	root.mainloop()

main()
