import multiprocessing
import numpy as np


class DataRecord():
    def __init__(self):
        self.raw_hex_buffer = multiprocessing.Queue()
        self.inflow_data_size = multiprocessing.Value('l', 0)   # 写入的数据量
        self.outflow_data_size = multiprocessing.Value('l', 0)  # 读出的数据量
        self.frame_data_buffer = multiprocessing.Queue()
        # 四路IQ信号
        self.sig_2D_matrix_channel_0 = multiprocessing.Queue()
        self.sig_2D_matrix_channel_1 = multiprocessing.Queue()
        self.sig_2D_matrix_channel_2 = multiprocessing.Queue()
        self.sig_2D_matrix_channel_3 = multiprocessing.Queue()
        self.hrrp_1d_array = multiprocessing.Queue()     # 存放一维HRRP像
        # 四路RD像
        self.RD_ch_0 = multiprocessing.Queue()  # 存放二维RD像，通道0
        self.RD_ch_1 = multiprocessing.Queue()  # 存放二维RD像，通道1
        self.RD_ch_2 = multiprocessing.Queue()  # 存放二维RD像，通道2
        self.RD_ch_3 = multiprocessing.Queue()  # 存放二维RD像，通道3
        self.RD_predetection = multiprocessing.Queue()  # 存放二维RD像
        self.time_wave = multiprocessing.Queue()         # 时域波形
        # 检测结果信息
        self.target_num = multiprocessing.Value('B', 0)     # 目标个数
        self.RD_index = multiprocessing.Queue()  # RD矩阵中的下标(i,j)
        self.RD_r_v_info = multiprocessing.Queue()  # RD矩阵中的距离、速度信息
        self.theta_distance_info = multiprocessing.Queue()  # 距离-角度信息
        self.X_Y_info = multiprocessing.Queue()  # XY坐标信息
        # 初始化
        self.target_num.value = 0
        init_array = np.array([[1, 2],[3, 4]])
        self.RD_r_v_info.put(init_array)
        self.theta_distance_info.put(init_array)
        self.X_Y_info.put(init_array)
        self.hrrp_1d_array.put(np.ones(128))
        init_array = range(64*64)
        init_array = np.array(init_array)
        init_array = np.reshape(init_array, (64, 64))
        self.RD_predetection.put(init_array)
        # self.RD_predetection.put(np.zeros([128,256]))


# #################################### 与数据传输有关的函数 ########################################################

    def raw_hex_buffer_size(self):
        """ 当前raw_data空间中的数据量大小 """
        return int(self.inflow_data_size.value - self.outflow_data_size.value)

    def put_into_raw_hex_buffer(self, hex_data):
        """ 将网口收到的bit stream数据添加到raw_data这个bytes数组中 """
        self.raw_hex_buffer.put(hex_data)
        self.inflow_data_size.value += len(hex_data)
        return

    def get_one_package_from_hex_buffer(self):
        data = self.raw_hex_buffer.get()
        self.outflow_data_size.value += len(data)
        return data

    def raw_hex_buffer_is_empty(self):
        return self.raw_hex_buffer.empty()

    def put_one_frame_data_to_frame_buffer(self, frame_data):
        """ 将一帧数据存入frame buffer中 """
        self.frame_data_buffer.put(frame_data)

    def get_one_frame_data_from_frame_buffer(self):
        frame_data = self.frame_data_buffer.get()
        return frame_data

    def frame_data_buffer_is_empty(self):
        return self.frame_data_buffer.empty()

# #################################### 与时域波形有关的函数 ########################################################

    def get_time_wave(self):
        time_wave = self.get_sig_2D_matrix_channel_1()
        time_wave = time_wave[0]
        return time_wave

    def update_sig_2D_matrix_channel_0(self, matrix_data):
        while not self.sig_2D_matrix_channel_0.empty():
            self.sig_2D_matrix_channel_0.get()
        self.sig_2D_matrix_channel_0.put(matrix_data)

    def get_sig_2D_matrix_channel_0(self):
        sig_2D_matrix_channel_0 = self.sig_2D_matrix_channel_0.get()
        self.sig_2D_matrix_channel_0.put(sig_2D_matrix_channel_0)
        return sig_2D_matrix_channel_0

    def update_sig_2D_matrix_channel_1(self, matrix_data):
        while not self.sig_2D_matrix_channel_1.empty():
            self.sig_2D_matrix_channel_1.get()
        self.sig_2D_matrix_channel_1.put(matrix_data)

    def get_sig_2D_matrix_channel_1(self):
        sig_2D_matrix_channel_1 = self.sig_2D_matrix_channel_1.get()
        self.sig_2D_matrix_channel_1.put(sig_2D_matrix_channel_1)
        return sig_2D_matrix_channel_1

    def update_sig_2D_matrix_channel_2(self, matrix_data):
        while not self.sig_2D_matrix_channel_2.empty():
            self.sig_2D_matrix_channel_2.get()
        self.sig_2D_matrix_channel_2.put(matrix_data)

    def get_sig_2D_matrix_channel_2(self):
        sig_2D_matrix_channel_2 = self.sig_2D_matrix_channel_2.get()
        self.sig_2D_matrix_channel_2.put(sig_2D_matrix_channel_2)
        return sig_2D_matrix_channel_2

    def update_sig_2D_matrix_channel_3(self, matrix_data):
        while not self.sig_2D_matrix_channel_3.empty():
            self.sig_2D_matrix_channel_3.get()
        self.sig_2D_matrix_channel_3.put(matrix_data)

    def get_sig_2D_matrix_channel_3(self):
        sig_2D_matrix_channel_3 = self.sig_2D_matrix_channel_3.get()
        self.sig_2D_matrix_channel_3.put(sig_2D_matrix_channel_3)
        return sig_2D_matrix_channel_3

# #################################### 与HRRP有关的函数 ########################################################

    def update_hrrp_1d_array(self, hrrp_data):
        while not self.hrrp_1d_array.empty():
            self.hrrp_1d_array.get()
        self.hrrp_1d_array.put(hrrp_data)

    def get_hrrp_1d_array(self):
        hrrp_data = self.hrrp_1d_array.get()
        self.hrrp_1d_array.put(hrrp_data)
        return hrrp_data

# #################################### 与RD二维矩阵有关的函数 ########################################################

    def update_RD_ch_0(self, rd_data):
        while not self.RD_ch_0.empty():
            self.RD_ch_0.get()
        self.RD_ch_0.put(rd_data)

    def get_RD_ch_0(self):
        RD_ch_0 = self.RD_ch_0.get()
        self.RD_ch_0.put(RD_ch_0)
        return RD_ch_0

    def update_RD_ch_1(self, rd_data):
        while not self.RD_ch_1.empty():
            self.RD_ch_1.get()
        self.RD_ch_1.put(rd_data)

    def get_RD_ch_1(self):
        RD_ch_1 = self.RD_ch_1.get()
        self.RD_ch_1.put(RD_ch_1)
        return RD_ch_1

    def update_RD_ch_2(self, rd_data):
        while not self.RD_ch_2.empty():
            self.RD_ch_2.get()
        self.RD_ch_2.put(rd_data)

    def get_RD_ch_2(self):
        RD_ch_2 = self.RD_ch_2.get()
        self.RD_ch_2.put(RD_ch_2)
        return RD_ch_2

    def update_RD_ch_3(self, rd_data):
        while not self.RD_ch_3.empty():
            self.RD_ch_3.get()
        self.RD_ch_3.put(rd_data)

    def get_RD_ch_3(self):
        RD_ch_3 = self.RD_ch_3.get()
        self.RD_ch_3.put(RD_ch_3)
        return RD_ch_3

    def update_RD_predetection(self, rd_data):
        while not self.RD_predetection.empty():
            self.RD_predetection.get()
        self.RD_predetection.put(rd_data)

    def get_RD_predetection(self):
        RD_predetection = self.RD_predetection.get()
        self.RD_predetection.put(RD_predetection)
        return RD_predetection

# #################################### 与CFAR检测有关的函数 ########################################################

    def update_target_num(self, num):
        self.target_num.value = num

    def get_target_num(self):
        return int(self.target_num.value)

    def update_RD_index(self, RD_index):
        while not self.RD_index.empty():
            self.RD_index.get()
        self.RD_index.put(RD_index)

    def get_RD_index(self):
        RD_index = self.RD_index.get()
        self.RD_index.put(RD_index)
        return RD_index

    def update_RD_r_v_info(self, RD_r_v_info):
        while not self.RD_r_v_info.empty():
            self.RD_r_v_info.get()
        self.RD_r_v_info.put(RD_r_v_info)

    def get_RD_r_v_info(self):
        RD_r_v_info = self.RD_r_v_info.get()
        self.RD_r_v_info.put(RD_r_v_info)
        return RD_r_v_info

# #################################### 与角度估计有关的函数 ########################################################

    def update_theta_distance_info(self, theta_distance_info):
        while not self.theta_distance_info.empty():
            self.theta_distance_info.get()
        self.theta_distance_info.put(theta_distance_info)

    def get_theta_distance_info(self):
        theta_distance_info = self.theta_distance_info.get()
        self.theta_distance_info.put(theta_distance_info)
        return theta_distance_info

    def update_X_Y_info(self, X_Y_info):
        while not self.X_Y_info.empty():
            self.X_Y_info.get()
        self.X_Y_info.put(X_Y_info)

    def get_X_Y_info(self):
        X_Y_info = self.X_Y_info.get()
        self.X_Y_info.put(X_Y_info)
        return X_Y_info
