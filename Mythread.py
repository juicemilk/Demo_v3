#coding:utf-8

"""
@author: xxy
@email: xyxie@buaa.edu.cn
@file: Mythread.py
@time: 2019/6/13 16:14
"""
from PyQt5 import QtCore
import numpy as np
import time
"""角度映射函数"""


def theta_map(x):
    return np.pi*(90 - x)/180

class Mythread(QtCore.QThread):
    def __init__(self,radar,showimage,flag):
        super(Mythread,self).__init__()
        self.radar=radar
        self.showimage=showimage
        self.flag=flag
        self.i=0
        print("创建线程")

    def run(self):
        print("启动线程")
        while self.flag:
            targets = self.radar.data_obj.get_target_num()
            self.i=self.i+1
            targets=self.i
            print(1)
            print(targets)
            range_velocity = self.radar.data_obj.get_RD_r_v_info()
            ranges = range_velocity[:, 0]
            velocitys = range_velocity[:, 1]

            position = self.radar.data_obj.get_X_Y_info()
            x_position = position[:, 0]
            y_position = position[:, 1]

            theta_r = self.radar.data_obj.get_theta_distance_info()
            theta_p = theta_r[:, 0]
            theta = np.array(list(map(theta_map, theta_p)))
            r = theta_r[:, 1]
            # print(theta)
            # print(r)
            self.showimage(targets,ranges,velocitys,x_position,y_position,theta,r)
            # time.sleep(100)

    def thread_stop_start(self,status):
        self.flag=status

