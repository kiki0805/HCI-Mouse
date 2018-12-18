import random
import matplotlib
import collections
import numpy as np
import matplotlib.pyplot as plt


class GraphicsManager:
    def __init__(self):
        self.lines = {}
        self.data = {}
        self.ax = plt.gca()
        plt.ion()
    
    def register(self, name, max_len, scatter=False):
        self.register_data(name, max_len)
        if scatter:
            self.register_scatter(name)
        else:
            self.register_plot(name)

    def register_plot(self, line_name):
        self.lines[line_name] = plt.plot([], [], self.get_random_color(), marker='.')[0]
    
    def register_scatter(self, line_name):
        self.lines[line_name] = plt.scatter([], [], c=self.get_random_color(), marker='x')

    def register_data(self, data_label, max_len):
        self.data[data_label] = collections.deque(maxlen=int(max_len))

    def update(self, name, point):
        if not point:
            return
        self.update_data(name, point)
        self.update_line(name)

    def update_data(self, data_label, point):
        self.data[data_label].append(point)

    def update_line(self, line_name):
        data = self.data[line_name]
        np_data = np.array(data)
        
        if type(self.lines[line_name]) == matplotlib.lines.Line2D:
            self.lines[line_name].set_xdata(np_data[:, 0])
            self.lines[line_name].set_ydata(np_data[:, 1])
        elif type(self.lines[line_name]) == matplotlib.collections.PathCollection:
            self.lines[line_name].set_offsets(np_data)
        else:
            raise Exception

        self.ax.set_xlim(np_data[:, 0].min(), np_data[:, 0].max())
        self.ax.set_ylim(128, 240)
        plt.draw() # plot new figure
        plt.pause(1e-17)

    @classmethod
    def get_random_color(self):
        return (random.random(), random.random(), random.random(), 1)
