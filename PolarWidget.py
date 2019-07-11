#coding:utf-8

"""
@author: xxy
@email: xyxie@buaa.edu.cn
@file: PolarWidget.py
@time: 2019/5/26 10:50
"""
import numpy as np
import matplotlib



matplotlib.use("Qt5Agg")


from PyQt5.QtWidgets import QSizePolicy


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


from matplotlib.figure import Figure


class polarwidget(FigureCanvas):
    def __init__(self, parent=None, width=15, height=10, dpi=150):

        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111,projection='polar')

        FigureCanvas.__init__(self, fig)

        self.setParent(parent)
        self.axes.set_thetamin(0)
        self.axes.set_thetamax(180)
        self.axes.set_thetagrids(np.linspace(0,180,7))
        self.axes.set_rlim(0,20)
        # self.axes.set_rgrids(np.linspace(0,100,6))

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
