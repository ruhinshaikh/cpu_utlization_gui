from typing import *
import datetime as dt
import sys
import os
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from psutil import cpu_percent,virtual_memory
import matplotlib as mpl
from matplotlib.pyplot import plot
import numpy as np

def cpu_average():
    return [cpu_percent()]

def memory_average():
    memory_usage=dict(virtual_memory()._asdict())
    return [memory_usage["percent"]]

class ApplicationWindow(QtWidgets.QMainWindow):
    '''
    The PyQt5 main window.

    '''
    def __init__(self):
        super().__init__()
        # 1. Window settings
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("CPU Utilization")
        self.frm = QtWidgets.QFrame(self)
        self.frm.setStyleSheet("QWidget { background-color:grey; }")
        self.lyt = QtWidgets.QVBoxLayout()
        self.frm.setLayout(self.lyt)
        self.setCentralWidget(self.frm)

        # 2. Place the matplotlib figure
        self.myFig = MyFigureCanvas(x_len=20, y_range=[0,100], interval=1000)
        self.lyt.addWidget(self.myFig)

        # 3. Show
        self.show()
        return

class MyFigureCanvas(FigureCanvas):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self, x_len:int, y_range:List, interval:int) -> None:
        '''
        :param x_len:       The nr of data points shown in one plot.
        :param y_range:     Range on y-axis.
        :param interval:    Get a new datapoint every .. milliseconds.

        '''
        super().__init__(mpl.figure.Figure())
        # Range settings
        self._x_len_ = x_len
        self._y_range_ = y_range

        # Store two lists _x_ and _y_

        self._x_ = list([dt.datetime.now().strftime('%H:%M:%S')])
        self._y_ = [cpu_average()]
        self._z_= [memory_average()]

        # Store a figure ax
        self._ax_ = self.figure.subplots()
        self._ax_.set_ylim(ymin=0, ymax=100) # added
        self._line_, = self._ax_.plot(self._x_, self._y_)
        # self.draw()
        self._line_, = self._ax_.plot(self._x_, self._z_)
        self.draw()


        # Initiate the timer
        self._timer_ = self.new_timer(interval, [(self._update_canvas_, (), {})])
        self._timer_.start()
        return

    def _update_canvas_(self) -> None:
        '''
        This function gets called regularly by the timer.

        '''
        self._x_.append(dt.datetime.now().strftime('%H:%M:%S')) # Add new datapoint to x
        self._y_.append(cpu_average()) # Add new datapoint to y
        self._z_.append(memory_average())         # Add new datapoint to z
        self._x_ = self._x_[-10:]                 # Truncate list x, limiting it to 10
        self._y_ = self._y_[-10:]                 # Truncate list y,limiting it to 10
        self._z_ = self._z_[-10:]                 # Truncate list z,limiting it to 10

        self._ax_.clear()                                   # Clear ax
        self._ax_.plot(self._x_, self._y_,color='green')   # Plot y(x)
        self._ax_.plot(self._x_, self._z_,color='blue')   # Plot y(x)
        self._ax_.set_title('CPU utilization percent per second')
        self._ax_.set_ylabel('CPU utilization percent')
        self._ax_.set_ylim(ymin=self._y_range_[0], ymax=self._y_range_[1])
        self._ax_.set_facecolor('xkcd:black')
        self.draw()

        self.update()
        self.flush_events()
        return


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    qapp.exec_()