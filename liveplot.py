import time
import queue
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FuncFormatter
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class LivePlotter(ttk.Frame):
    def __init__(
        self,
        root,
        time_scale,
        labels,
        colors,
        update_interval=50,
        line_width=2,
        **kwargs
    ):
        assert len(labels) == len(colors)
        super().__init__(root, **kwargs)

        self.time_scale = time_scale
        self.update_interval = update_interval

        # Set up Matplotlib
        self.fig, self.ax = plt.subplots()
        self.x_data = []
        self.y_data = [[] for _ in colors]

        self.lines = []
        for label, color in zip(labels, colors):
            self.lines.append(
                self.ax.plot([], [], lw=line_width, label=label, color=color)[0]
            )

        # Embed Matplotlib plot in Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)

        # Configure animation
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_plot,
            init_func=self.init,
            blit=False,
            interval=self.update_interval,
            cache_frame_data=False,
        )

        self.start = time.time()

        self.value_queue = queue.Queue()

        self.ax.legend()

        self.min_y = float("inf")
        self.max_y = float("-inf")

    def plot(self, data_points):
        current_time = time.time() - self.start
        self.value_queue.put((current_time, data_points))

    def init(self):
        self.ax.set_xlim(0, self.time_scale)
        for line in self.lines:
            line.set_data([], [])
        return self.lines

    def update_plot(self, frame):
        while not self.value_queue.empty():
            x, y_points = self.value_queue.get()
            self.x_data.append(x)
            for i, y in enumerate(y_points):
                self.y_data[i].append(y)

        if len(self.x_data) == 0:
            return

        while max(self.x_data) - min(self.x_data) > self.time_scale:
            self.x_data.pop(0)
            for y_list in self.y_data:
                y_list.pop(0)

        xmax = max(self.time_scale, max(self.x_data))

        self.ax.set_xlim(xmax - self.time_scale, xmax)

        # Dynamically adjust y-axis limits based on all lines' data
        all_y_data = [y for y_list in self.y_data for y in y_list]

        if all_y_data:
            min_y = min(all_y_data)
            max_y = max(all_y_data)

            if min_y < self.min_y:
                self.min_y = min_y
            if max_y > self.max_y:
                self.max_y = max_y

            gap = max(1, 0.1 * abs(self.max_y - self.min_y))
            self.ax.set_ylim(self.min_y - gap, self.max_y + gap)

        for line, y_list in zip(self.lines, self.y_data):
            line.set_data(self.x_data, y_list)
        return self.lines

    def reset_view(self):
        self.min_y = float("inf")
        self.max_y = -float("inf")

    def __del__(self):
        if self.ani.event_source is not None:
            self.ani.event_source.stop()
