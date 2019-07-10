#coding:utf-8

"""
@author: xxy
@email: xyxie@buaa.edu.cn
@file: ScatterWidget2.py
@time: 2019/5/29 16:46
"""

import matplotlib



matplotlib.use("Qt5Agg")


from PyQt5.QtWidgets import QSizePolicy


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


from matplotlib.figure import Figure



class scatterwidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)

        self.setParent(parent)


        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
