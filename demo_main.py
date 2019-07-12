#coding:utf-8

"""
@author: xxy
@email: xyxie@buaa.edu.cn
@file: demo_main.py
@time: 2019/5/26 11:19
"""
from demo import Ui_MainWindow
from PyQt5 import QtWidgets,QtCore,QtGui
import sys,cv2
from PyQt5.QtCore import *
from radar_api import RadarAPI
import numpy as np
from Mythread import Mythread
"""角度映射函数"""


def theta_map(x):
    return 0.5*np.pi-x

class Demo(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Demo, self).__init__()
        self.setupUi(self)
        self.CAM_NUM = 1
        self.cap = cv2.VideoCapture()
        self.timeslot()
        self.radar=RadarAPI()
        self.read_parameter()
        self.axes_init()
        # self.i=0
        self.MyThread = Mythread(self.radar,self.updateimage)


    """雷达参数读取"""
    def read_parameter(self):
        self.radar_freq="77GHz"
        self.radar_width=self.radar.radar_para_obj.get_BW_in_MHz()
        self.r_max=self.radar.radar_para_obj.get_R_max()
        self.r_res=self.radar.radar_para_obj.get_R_gap()
        self.v_max = self.radar.radar_para_obj.get_V_max()
        self.v_res = self.radar.radar_para_obj.get_V_gap()

        self.freq_line.setText(self.radar_freq)
        self.width_line.setText(str(self.radar_width)+'MHz')
        self.r_max_line.setText(str(round(self.r_max,2))+'m')
        self.r_res_line.setText(str(round(self.r_res,2))+'m')
        self.v_max_line.setText(str(round(self.v_max,2))+'m/s')
        self.v_res_line.setText(str(round(self.v_res,2))+'m/s')
    """实例定时器并信号槽连接"""
    def timeslot(self):
        self.cameratimer = QtCore.QTimer(self)
        self.cameratimer.timeout.connect(self.show_camera)
        # self.plottimer=QtCore.QTimer(self)
        # self.plottimer.timeout.connect(self.updateimage)

    """绘图坐标轴初始化"""
    def axes_init(self):

        # self.rangedoppler.axes.cla()
        # self.rangedoppler.axes.set_xlim(-10,10)
        # self.rangedoppler.axes.spines['right'].set_color('none')
        # self.rangedoppler.axes.spines['top'].set_color('none')
        # self.rangedoppler.axes.xaxis.set_ticks_position('bottom')
        # self.rangedoppler.axes.yaxis.set_ticks_position('left')
        # self.rangedoppler.axes.spines['bottom'].set_position(('data', 0))
        # self.rangedoppler.axes.spines['left'].set_position(('data', 0))
        # self.rangedoppler.axes.set_ylim(0,30)
        # self.rangedoppler.axes.set_xlabel("Velocity(m/s)")
        # self.rangedoppler.axes.set_ylabel("Range(m)")
        # data=np.array([[0,1,0],[0,0,0],[0,0,0]])
        # self.rangedopplersc=self.rangedoppler.axes.imshow(data,extent=[0,100,0,100],cmap='Blues')

        self.radarplot.axes.cla()
        self.radarplot.axes.set_thetamin(20)
        self.radarplot.axes.set_thetamax(160)
        self.radarplot.axes.set_thetagrids(np.linspace(20,160,7))
        self.radarplot.axes.set_rlim(0,self.r_max)
        self.radarplot.axes.set_rgrids(np.linspace(0,self.r_max,int(self.r_max/10+1)))
        self.radarsc=self.radarplot.axes.scatter([],[])

        self.xyplot.axes.cla()
        self.xyplot.axes.set_xlim(-self.r_max/2, self.r_max/2)
        self.xyplot.axes.spines['right'].set_color('none')
        self.xyplot.axes.spines['top'].set_color('none')
        self.xyplot.axes.xaxis.set_ticks_position('bottom')
        self.xyplot.axes.yaxis.set_ticks_position('left')
        self.xyplot.axes.spines['bottom'].set_position(('data', 0))
        self.xyplot.axes.spines['left'].set_position(('data', 0))
        self.xyplot.axes.set_ylim(0,self.r_max)
        self.xyplot.axes.set_xlabel("Range(m)")
        self.xyplot.axes.set_ylabel("Range(m)")
        self.xyplotsc = self.xyplot.axes.scatter([], [])


    """相机开关按钮"""
    @pyqtSlot()
    def on_camerapushButton_clicked(self):
        if self.cameratimer.isActive() == False:

            flag = self.cap.open(self.CAM_NUM)
            if flag == False:

                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,

                                                    defaultButton=QtWidgets.QMessageBox.Ok)

            else:
                self.cameratimer.start(30)
                self.camerapushButton.setText(u'关闭相机')



        else:
            self.cameratimer.stop()

            self.cap.release()

            self.camera.clear()

            self.camerapushButton.setText(u'打开相机')

    """开始绘图"""
    @pyqtSlot()
    def on_plotpushButton_clicked(self):
        # if self.plottimer.isActive() == False:
        #     self.plotpushButton.setText(u'停止绘图')
        #     self.plottimer.start(100)
        # else:
        #     self.plotpushButton.setText(u'开始绘图')
        #     self.i=0
        #     self.plottimer.stop()
        if self.MyThread.isRunning() == False:
            self.plotpushButton.setText(u'停止绘图')
            self.MyThread.thread_stop_start(True)
            # self.i=0
            self.MyThread.start()
        else:
            self.plotpushButton.setText(u'开始绘图')
            self.MyThread.thread_stop_start(False)
            self.MyThread.quit()

    """图片显示"""
    def show_camera(self):
        flag, self.image = self.cap.read()
        show = cv2.resize(self.image, (1200,800))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.camera.setPixmap(QtGui.QPixmap.fromImage(showImage))


    """绘图更新"""
    def updateimage(self,rd,x,y,theta,r):
        # self.i=self.i+1
        # print('当前帧数：'+str(self.i))
        # self.plottimer.stop()
        # print(self.information_groupBox.size().width())
        # self.i=self.i+1
        # self.freq_line.setText(str(self.i))
        self.rdplot.axes.cla()

        self.rdplot.axes.imshow(rd, extent=[0, self.r_max,-self.v_max, self.v_max])
        self.rdplot.draw()
        self.xyplotsc.set_offsets(np.c_[x, y])
        self.xyplot.draw()
        self.radarsc.set_offsets(np.c_[theta,r])
        self.radarplot.draw()
        # self.plottimer.start(100)
        # print(self.location_groupBox_4.size())




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Demo()
    myshow.show()
    sys.exit(app.exec_())