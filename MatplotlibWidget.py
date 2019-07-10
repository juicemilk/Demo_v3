#coding:utf-8

"""
@author: xxy
@email: xyxie@buaa.edu.cn
@file: MatplotlibWidget.py
@time: 2019/3/12 20:09
"""

import matplotlib



matplotlib.use("Qt5Agg")


from PyQt5.QtWidgets import QSizePolicy


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


from matplotlib.figure import Figure


class matplotlibwidget(FigureCanvas):
    def __init__(self, parent=None, width=10, height=8, dpi=100):

        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)

        self.setParent(parent)
        # self.axes.set_xlim(0,128)
        # self.axes.set_ylim(0,10)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
