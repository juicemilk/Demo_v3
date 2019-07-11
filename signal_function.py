import numpy as np


class SignalFunc():
    def  __init__(self):
        self.__data_obj = None
        self.__radar_para_obj = None
        self.__samples_in_chirp = None
        self.__chirps_in_frame = None
        self.__num_of_IQ_data_per_frame = None
        self.__rx_0_matrix = None
        self.__rx_1_matrix = None
        self.__rx_2_matrix = None
        self.__rx_3_matrix = None
        self.__RD_0 = None
        self.__RD_1 = None
        self.__RD_2 = None
        self.__RD_3 = None
        self.__RD_sum = None
        self.__HRRP = None

    def get_handle(self, global_obj):
        self.__data_obj = global_obj.data_obj
        self.__radar_para_obj = global_obj.radar_para_obj
        self.__samples_in_chirp = self.__radar_para_obj.get_samples_in_chirp()
        self.__chirps_in_frame = self.__radar_para_obj.get_chirps_in_frame()
        self.__num_of_IQ_data_per_frame = self.__samples_in_chirp * self.__chirps_in_frame * 4  # 4 channel

    def signal_processing_start(self):
        self.signal_prepare()
        self.compute_rd_2d_array()
        self.compute_hrrp_1d_array()
        self.cfar_detect()
        self.angle_estimation()
        # print('目标数：')
        # target_num = self.__data_obj.get_target_num()
        # print(target_num)
        # print('RD图中的LOS方向距离、速度：')
        # RD_r_v_info = self.__data_obj.get_RD_r_v_info()
        # print(RD_r_v_info)
        # print('角度、径向距离信息：')
        # theta_distance_info = self.__data_obj.get_theta_distance_info()
        # print(theta_distance_info)
        # print('X-Y坐标信息：')
        # X_Y_info = self.__data_obj.get_X_Y_info()
        # print(X_Y_info)

    def signal_prepare(self):
        """ 将一维序列的complex转成4路complex_matrix """
        frame_data = self.__data_obj.get_one_frame_data_from_frame_buffer()
        data_len = self.__num_of_IQ_data_per_frame
        # 开始处理
        rx_matrix_0 = frame_data[0:data_len:4]
        rx_matrix_1 = frame_data[1:data_len:4]
        rx_matrix_2 = frame_data[2:data_len:4]
        rx_matrix_3 = frame_data[3:data_len:4]
        # 重构
        samples_in_chirp = self.__samples_in_chirp
        chirps_in_frame = self.__chirps_in_frame
        rx_matrix_0 = np.reshape(rx_matrix_0, (chirps_in_frame, samples_in_chirp))
        rx_matrix_1 = np.reshape(rx_matrix_1, (chirps_in_frame, samples_in_chirp))
        rx_matrix_2 = np.reshape(rx_matrix_2, (chirps_in_frame, samples_in_chirp))
        rx_matrix_3 = np.reshape(rx_matrix_3, (chirps_in_frame, samples_in_chirp))
        self.__rx_0_matrix = rx_matrix_0
        self.__rx_1_matrix = rx_matrix_1
        self.__rx_2_matrix = rx_matrix_2
        self.__rx_3_matrix = rx_matrix_3

    def compute_hrrp_1d_array(self):
        """ 对self.data_obj进行操作，此操作会更新self.__data_obj.hrrp_1d_array """
        RD_matrix = self.__RD_sum
        hrrp = np.sum(RD_matrix, 0)
        self.__HRRP = hrrp
        self.__data_obj.update_hrrp_1d_array(hrrp)

    def compute_rd_2d_array(self):
        N_FFT_1 = self.__radar_para_obj.get_N_FFT_1()
        N_FFT_2 = self.__radar_para_obj.get_N_FFT_2()
        # 计算RD_0
        rx_0 = self.__rx_0_matrix
        rx_0 = self.remove_static_target(rx_0)
        RD_0 = np.fft.fft2(rx_0, [N_FFT_2, N_FFT_1])
        RD_0 = np.fft.fftshift(RD_0)
        # 计算RD_1
        rx_1 = self.__rx_1_matrix
        rx_1 = self.remove_static_target(rx_1)
        RD_1 = np.fft.fft2(rx_1, [N_FFT_2, N_FFT_1])
        RD_1 = np.fft.fftshift(RD_1)
        # 计算RD_2
        rx_2 = self.__rx_2_matrix
        rx_2 = self.remove_static_target(rx_2)
        RD_2 = np.fft.fft2(rx_2, [N_FFT_2, N_FFT_1])
        RD_2 = np.fft.fftshift(RD_2)
        # 计算RD_3
        rx_3 = self.__rx_3_matrix
        rx_3 = self.remove_static_target(rx_3)
        RD_3 = np.fft.fft2(rx_3, [N_FFT_2, N_FFT_1])
        RD_3 = np.fft.fftshift(RD_3)
        # 计算RD_predetection
        RD_sum = abs(RD_0) + abs(RD_1) + abs(RD_2) + abs(RD_3) + 1
        # 更新
        self.__RD_0 = RD_0
        self.__RD_1 = RD_1
        self.__RD_2 = RD_2
        self.__RD_3 = RD_3
        self.__RD_sum = RD_sum
        half_N_FFT_1 = int(N_FFT_1/2)
        self.__data_obj.update_RD_predetection(RD_sum[:, half_N_FFT_1:N_FFT_1])

    def remove_static_target(self, rx_sig):
        samples_in_chirp = np.shape(rx_sig)[1]
        chirps_in_frame = np.shape(rx_sig)[0]
        for n in range(chirps_in_frame):
            chirp = rx_sig[n, :]
            mean_level = np.mean(chirp)
            rx_sig[n, :] = rx_sig[n, :] - mean_level
        for m in range(samples_in_chirp):
            doppler = rx_sig[:, m]
            mean_level = np.mean(doppler)
            rx_sig[:, m] = rx_sig[:, m] - mean_level
        return rx_sig

    def cfar_detect(self):
        # 参数初始化
        cfar_index_1d = 0
        cfar_index_2d = 6
        R_prot = 1            # 距离保护单元范围（米）
        R_ref = 2               # 距离参考单元范围（米）
        R_gap = self.__radar_para_obj.get_R_gap()
        R_prot_unit = int(np.ceil(R_prot/R_gap))
        R_ref_unit = int(np.ceil(R_ref/R_gap))
        V_prot = 1            # 速度保护单元范围（米/秒）
        V_ref = 2               # 速度参考单元范围（米/秒）
        V_gap = self.__radar_para_obj.get_V_gap()
        V_prot_unit = int(np.ceil(V_prot/V_gap))
        V_ref_unit = int(np.ceil(V_ref / V_gap))
        RD_matrix = self.__RD_sum
        N_FFT_1 = self.__radar_para_obj.get_N_FFT_1()     # samples_in_chirp
        N_FFT_2 = self.__radar_para_obj.get_N_FFT_2()     # chirps_in_frame
        R_max = self.__radar_para_obj.get_R_max()
        V_max = self.__radar_para_obj.get_V_max()
        range_axis = np.linspace(-R_max, R_max - 2 * R_max / N_FFT_1, N_FFT_1)
        velocity_axis = np.linspace(-V_max, V_max - 2 * V_max / N_FFT_2, N_FFT_2)
        M = N_FFT_1
        N = N_FFT_2
        half_M = int(M / 2)
        half_N = int(N / 2)
        # 目标信息初始化
        target_num = 0
        target_RD_index = []
        target_RD_r_v_info = []
        target_amp = []
        # 开始计算
        expand_matrix = self.create_expand_matrix(RD_matrix)
        expand_HRRP = np.sum(expand_matrix, 0)
        # i=range(M, M+half_M)是正距离轴
        for i in range(M, M+half_M):
            range_detect_flag = self.os_cfar_1d(expand_HRRP, i, cfar_index_1d, R_prot_unit, R_ref_unit)
            if range_detect_flag:
                # j=range(half_N, N+half_N)是全部多普勒轴，range(N, N+half_N)是全部多普勒轴
                for j in range(N, N+half_N):
                    global_detect_flag = self.os_cfar_2d(expand_matrix, cfar_index_2d, i, j, R_prot_unit, R_ref_unit, V_prot_unit, V_ref_unit)
                    if global_detect_flag:
                        target_num += 1
                        target_RD_index.append([i-half_M, j-half_N])
                        target_range = range_axis[i-half_M]
                        target_velocity = velocity_axis[j-half_N]
                        target_RD_r_v_info.append([target_range, target_velocity])
        RD_index = np.array(target_RD_index)
        RD_r_v_info = np.array(target_RD_r_v_info)
        self.__data_obj.update_target_num(target_num)
        self.__data_obj.update_RD_index(RD_index)
        self.__data_obj.update_RD_r_v_info(RD_r_v_info)

    def os_cfar_1d(self, expand_HRRP, i, cfar_index, protection_unit, reference_unit):
        os_index = 0.75
        front_part = expand_HRRP[i - protection_unit - reference_unit:i - protection_unit]
        back_part = expand_HRRP[i + protection_unit + 1:i + protection_unit + reference_unit + 1]
        ordered_array = np.append(front_part, back_part)
        ordered_array = np.sort(ordered_array)
        noise_level = ordered_array[int(os_index * ordered_array.size)]
        if 10*np.log10(expand_HRRP[i]) > 10*np.log10(noise_level)+cfar_index:
            return True
        else:
            return False

    def os_cfar_2d(self, expand_matrix, cfar_index_2d, i, j, R_prot_unit, R_ref_unit, V_prot_unit, V_ref_unit):
        os_index = 0.75
        ordered_array = np.array([])
        for m in range(i-R_prot_unit-R_ref_unit, i-R_prot_unit):
            doppler = expand_matrix[j-V_prot_unit-V_ref_unit:j+V_prot_unit+V_ref_unit+1, m]
            ordered_array = np.append(ordered_array, doppler)
        for m in range(i-R_prot_unit, i+R_prot_unit+1):
            doppler_left = expand_matrix[j-V_prot_unit-V_ref_unit:j-V_prot_unit, m]
            doppler_right = expand_matrix[j+V_prot_unit+1:j+V_prot_unit+V_ref_unit+1, m]
            ordered_array = np.hstack((ordered_array, doppler_left, doppler_right))
        for m in range(i+R_prot_unit+1, i+R_prot_unit+R_ref_unit+1):
            doppler = expand_matrix[j - V_prot_unit - V_ref_unit:j + V_prot_unit + V_ref_unit + 1, m]
            ordered_array = np.append(ordered_array, doppler)
        # 排序与噪声估计
        ordered_array = np.sort(ordered_array)
        noise_level = ordered_array[int(os_index * ordered_array.size)]
        if 10*np.log10(expand_matrix[j, i]) > 10*np.log10(noise_level)+cfar_index_2d:
            return True
        else:
            return False

    def create_expand_matrix(self, RD_matrix):
        M = RD_matrix.shape[1]
        N = RD_matrix.shape[0]
        half_M = int(M / 2)
        half_N = int(N / 2)
        p1 = RD_matrix[0:half_N, 0:half_M]
        p2 = RD_matrix[half_N:N, 0:half_M]
        p3 = RD_matrix[0:half_N, half_M:M]
        p4 = RD_matrix[half_N:N, half_M:M]
        c1 = np.hstack((p4, p2, p4, p2))
        c2 = np.hstack((p3, p1, p3, p1))
        c3 = np.hstack((p4, p2, p4, p2))
        c4 = np.hstack((p3, p1, p3, p1))
        expand_matrix = np.vstack((c1, c2, c3, c4))
        return expand_matrix

    def cluster(self, predetection_RD_matrix, i, j):
        # 设定聚类范围
        R_ref = 1  # 距离参考单元范围（米）
        R_gap = self.__radar_para_obj.get_R_gap()
        R_ref_unit = int(np.ceil(R_ref / R_gap))
        V_ref = 1  # 速度参考单元范围（米/秒）
        V_gap = self.__radar_para_obj.get_V_gap()
        V_ref_unit = int(np.ceil(V_ref / V_gap))
        # 开始聚类
        M = predetection_RD_matrix.shape[1]  # samples_in_chirp
        N = predetection_RD_matrix.shape[0]  # chirps_in_frame
        half_M = int(M / 2)
        half_N = int(N / 2)
        range_array = predetection_RD_matrix[j, half_M:M]
        range_array = np.append(range_array, predetection_RD_matrix[j, :])
        range_array = np.append(range_array, predetection_RD_matrix[j, 0:half_M])
        doppler_array = predetection_RD_matrix[half_N:N, i]
        doppler_array = np.append(doppler_array, predetection_RD_matrix[:, i])
        doppler_array = np.append(doppler_array, predetection_RD_matrix[0:half_N, i])
        range_front_part = range_array[i + half_M - R_ref_unit:i + half_M]
        range_back_part = range_array[i + half_M + 1:i + half_M + R_ref_unit + 1]
        doppler_front_part = doppler_array[j + half_N - V_ref_unit:j + half_N]
        doppler_back_part = doppler_array[j + half_N + 1:j + half_N + V_ref_unit + 1]
        neighbor_array = np.append(range_front_part, range_back_part)
        neighbor_array = np.append(neighbor_array, doppler_front_part)
        neighbor_array = np.append(neighbor_array, doppler_back_part)
        flag = True
        val = predetection_RD_matrix[j,i]
        for neighbor in neighbor_array:
            if val < neighbor:
                flag = False
                break
        return flag

    def angle_estimation(self):
        # 计算参数（距离轴、空间轴）
        N_FFT_1 = self.__radar_para_obj.get_N_FFT_1()  # samples_in_chirp
        R_max = self.__radar_para_obj.get_R_max()
        LOS_range_axis = np.linspace(-R_max, R_max - 2*R_max / N_FFT_1, N_FFT_1)
        N_FFT_3 = 256
        spatial_omega_axis = np.arange(int(-N_FFT_3 / 2), int(N_FFT_3 / 2))     # 空间频率轴
        spatial_theta_rad_axis = np.arcsin(2 * spatial_omega_axis / N_FFT_3)
        target_num = self.__data_obj.get_target_num()
        theta_distance_info = []
        X_Y_info = []
        # 多RD帧的角度估计
        RD_0 = self.__RD_0
        RD_1 = self.__RD_1
        RD_2 = self.__RD_2
        RD_3 = self.__RD_3
        RD_index = self.__data_obj.get_RD_index()
        for n in range(target_num):
            RD_idx = RD_index[n]
            angle_phase_array = []
            angle_phase_array.append(RD_0[RD_idx[1], RD_idx[0]])
            angle_phase_array.append(RD_1[RD_idx[1], RD_idx[0]])
            angle_phase_array.append(RD_2[RD_idx[1], RD_idx[0]])
            angle_phase_array.append(RD_3[RD_idx[1], RD_idx[0]])
            angle_fft = np.fft.fft(angle_phase_array, N_FFT_3)
            angle_fft = abs(np.fft.fftshift(angle_fft))         # 空间维FFT结果
            max_index = np.argmax(angle_fft)                    # 找到空间维FFT的最大值下标
            theta_rad = spatial_theta_rad_axis[max_index]       # 由最大值下标，在空间轴中确定角度
            LOS_range = LOS_range_axis[RD_idx[0]]         # 由RD矩阵的(i,j)信息，找到LOS距离
            radial_distance = LOS_range / np.cos(theta_rad)     # 由LOS距离求出点到点的径向距离
            theta_distance_info.append([theta_rad, radial_distance])    # 记录距离-角度信息
            x_pos = radial_distance * np.sin(theta_rad)         # 求出x位置
            y_pos = radial_distance * np.cos(theta_rad)         # 求出y位置
            X_Y_info.append([x_pos, y_pos])                     # 记录X-Y信息
        theta_distance_info = np.array(theta_distance_info)
        X_Y_info = np.array(X_Y_info)
        self.__data_obj.update_theta_distance_info(theta_distance_info)
        self.__data_obj.update_X_Y_info(X_Y_info)
