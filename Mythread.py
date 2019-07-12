#coding:utf-8

"""
@author: xxy
@email: xyxie@buaa.edu.cn
@file: Mythread.py
@time: 2019/6/13 16:14
"""
from PyQt5 import QtCore
import numpy as np
"""角度映射函数"""


def theta_map(x):
    return 0.5*np.pi-x

class Mythread(QtCore.QThread):
    def __init__(self,radar,updateimage):
        QtCore.QThread.__init__(self)
        self.radar=radar
        self.showimage=updateimage
        self.flag=True
        print("创建线程")

    def run(self):
        print("启动线程")
        while self.flag:
            rd = self.radar.data_obj.get_RD_predetection()
            x_y = self.radar.data_obj.get_X_Y_info()
            if len(x_y) != 0:
                x = x_y[:, 0]
                y = x_y[:, 1]
                theta_r = self.radar.data_obj.get_theta_distance_info()
                theta_p = theta_r[:, 0]
                theta = np.array(list(map(theta_map, theta_p)))
                r = theta_r[:, 1]
            else:
                x=np.array([0])
                y=np.array([100])
                theta=np.array([0])
                r=np.array([100])
            self.showimage(rd, x, y, theta, r)


    def thread_stop_start(self,status):
        self.flag=status

