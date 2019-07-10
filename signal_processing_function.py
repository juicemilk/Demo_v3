import numpy as np


class SignalProcessing():
    def __init__(self):
        self.__data_obj = None
        self.__radar_para_obj = None
        self.__samples_in_chirp = None
        self.__chirps_in_frame = None

    def get_handle(self, global_obj):
        self.__data_obj = global_obj.data_obj
        self.__radar_para_obj = global_obj.radar_para_obj

    def signal_processing_start(self):
        self.compute_hrrp_1d_array()
        self.compute_rd_2d_array()
        self.cfar_detect()
        self.angle_estimation()
        print('目标数：')
        target_num = self.__data_obj.get_target_num()
        print(target_num)
        # print('RD图中的LOS方向距离、速度：')
        # RD_r_v_info = self.__data_obj.get_RD_r_v_info()
        # print(RD_r_v_info)
        # print('角度、径向距离信息：')
        # theta_distance_info = self.__data_obj.get_theta_distance_info()
        # print(theta_distance_info)
        # print('X-Y坐标信息：')
        # X_Y_info = self.__data_obj.get_X_Y_info()
        # print(X_Y_info)

    def compute_hrrp_1d_array(self):
        """ 对self.data_obj进行操作，此操作会更新self.__data_obj.hrrp_1d_array """
        input_data = self.__data_obj.get_time_wave()
        hrrp = np.fft.fft(input_data)
        hrrp = abs(np.fft.fftshift(hrrp))
        self.__data_obj.update_hrrp_1d_array(hrrp)

    def compute_rd_2d_array(self):
        # 计算RD_0
        RD_0 = self.__data_obj.get_sig_2D_matrix_channel_0()
        RD_0 = np.fft.fft2(RD_0)
        RD_0 = np.fft.fftshift(RD_0)
        # 计算RD_1
        RD_1 = self.__data_obj.get_sig_2D_matrix_channel_1()
        RD_1 = np.fft.fft2(RD_1)
        RD_1 = np.fft.fftshift(RD_1)
        # 计算RD_2
        RD_2 = self.__data_obj.get_sig_2D_matrix_channel_2()
        RD_2 = np.fft.fft2(RD_2)
        RD_2 = np.fft.fftshift(RD_2)
        # 计算RD_3
        RD_3 = self.__data_obj.get_sig_2D_matrix_channel_3()
        RD_3 = np.fft.fft2(RD_3)
        RD_3 = np.fft.fftshift(RD_3)
        # 计算RD_predetection
        RD_predetection = abs(RD_0) + abs(RD_1) + abs(RD_2) + abs(RD_3)
        # 更新
        self.__data_obj.update_RD_ch_0(RD_0)
        self.__data_obj.update_RD_ch_1(RD_1)
        self.__data_obj.update_RD_ch_2(RD_2)
        self.__data_obj.update_RD_ch_3(RD_3)
        self.__data_obj.update_RD_predetection(RD_predetection)

    def cfar_detect(self):
        range_cfar_index = 1
        global_cfar_index = 3
        protection_unit = 1
        reference_unit = 5
        predetection_RD_matrix = self.__data_obj.get_RD_predetection()
        N_FFT_1 = self.get_N_FFT_1()     # samples_in_chirp
        N_FFT_2 = self.get_N_FFT_2()     # chirps_in_frame
        R_max = self.get_R_max()
        V_max = self.get_V_max()
        target_num = 0
        target_RD_index = []
        target_RD_r_v_info = []
        range_axis = np.linspace(-R_max, R_max - R_max / N_FFT_1, N_FFT_1)
        velocity_axis = np.linspace(-V_max, V_max - V_max / N_FFT_2, N_FFT_2)
        HRRP = np.sum(predetection_RD_matrix, 0)
        for i in range(N_FFT_1):
            range_detect_flag = self.os_cfar_1d(HRRP, i, range_cfar_index, protection_unit, reference_unit)
            if range_detect_flag:
                for j in range(N_FFT_2):
                    global_detect_flag = self.os_cfar_2d(predetection_RD_matrix, i, j, global_cfar_index, protection_unit, reference_unit)
                    if global_detect_flag:
                        target_num += 1
                        target_RD_index.append([i, j])
                        target_range = range_axis[i]
                        target_velocity = velocity_axis[j]
                        target_RD_r_v_info.append([target_range, target_velocity])
        RD_index = np.array(target_RD_index)
        RD_r_v_info = np.array(target_RD_r_v_info)
        self.__data_obj.update_target_num(target_num)
        self.__data_obj.update_RD_index(RD_index)
        self.__data_obj.update_RD_r_v_info(RD_r_v_info)

    def os_cfar_1d(self, obj_array, i, cfar_index, protection_unit, reference_unit):
        os_index = 3/4
        M = obj_array.size
        half_M = int(M/2)
        temp_array = obj_array[half_M:M]
        temp_array = np.append(temp_array, obj_array)
        temp_array = np.append(temp_array, obj_array[0:half_M])
        front_part = temp_array[i + half_M - protection_unit - reference_unit:i + half_M - protection_unit]
        back_part = temp_array[i + half_M + protection_unit + 1:i + half_M + protection_unit + reference_unit + 1]
        ordered_array = np.append(front_part, back_part)
        ordered_array = np.sort(ordered_array)
        noise_level = ordered_array[int(os_index * ordered_array.size)]
        if obj_array[i] > cfar_index*noise_level:
            return True
        else:
            return False

    def os_cfar_2d(self, predetection_RD_matrix, i, j, cfar_index, protection_unit, reference_unit):
        os_index = 3/4
        M = predetection_RD_matrix.shape[1]  # samples_in_chirp
        N = predetection_RD_matrix.shape[0]  # chirps_in_frame
        half_M = int(M/2)
        half_N = int(N/2)
        range_array = predetection_RD_matrix[j, half_M:M]
        range_array = np.append(range_array, predetection_RD_matrix[j, :])
        range_array = np.append(range_array, predetection_RD_matrix[j, 0:half_M])
        doppler_array = predetection_RD_matrix[half_N:N, i]
        doppler_array = np.append(doppler_array, predetection_RD_matrix[:, i])
        doppler_array = np.append(doppler_array, predetection_RD_matrix[0:half_N, i])
        range_front_part = range_array[i + half_M - protection_unit - reference_unit:i + half_M - protection_unit]
        range_back_part = range_array[i + half_M + protection_unit + 1:i + half_M + protection_unit + reference_unit + 1]
        doppler_front_part = doppler_array[j + half_N - protection_unit - reference_unit:j + half_N - protection_unit]
        doppler_back_part = doppler_array[j + half_N + protection_unit + 1:j + half_N + protection_unit + reference_unit + 1]
        ordered_array = np.append(range_front_part, range_back_part)
        ordered_array = np.append(ordered_array, doppler_front_part)
        ordered_array = np.append(ordered_array, doppler_back_part)
        ordered_array = np.sort(ordered_array)
        noise_level = ordered_array[int(os_index * ordered_array.size)]
        if predetection_RD_matrix[j,i] > cfar_index*noise_level:
            return True
        else:
            return False

    def angle_estimation(self):
        # 计算参数（距离轴、空间轴）
        N_FFT_1 = self.get_N_FFT_1()  # samples_in_chirp
        R_max = self.get_R_max()
        LOS_range_axis = np.linspace(-R_max, R_max - R_max / N_FFT_1, N_FFT_1)
        N_FFT_3 = 256
        spatial_omega_axis = np.arange(int(-N_FFT_3 / 2), int(N_FFT_3 / 2))     # 空间频率轴
        spatial_theta_rad_axis = np.arcsin(2 * spatial_omega_axis / N_FFT_3)
        target_num = self.__data_obj.get_target_num()
        theta_distance_info = []
        X_Y_info = []
        # 多RD帧的角度估计
        RD_0 = self.__data_obj.get_RD_ch_0()
        RD_1 = self.__data_obj.get_RD_ch_1()
        RD_2 = self.__data_obj.get_RD_ch_2()
        RD_3 = self.__data_obj.get_RD_ch_3()
        RD_index = self.__data_obj.get_RD_index()
        for n in range(target_num):
            cur_RD_index = RD_index[n]
            angle_phase_array = []
            angle_phase_array.append(RD_0[cur_RD_index[1], cur_RD_index[0]])
            angle_phase_array.append(RD_1[cur_RD_index[1], cur_RD_index[0]])
            angle_phase_array.append(RD_2[cur_RD_index[1], cur_RD_index[0]])
            angle_phase_array.append(RD_3[cur_RD_index[1], cur_RD_index[0]])
            angle_fft = np.fft.fft(angle_phase_array, N_FFT_3)
            angle_fft = abs(np.fft.fftshift(angle_fft))         # 空间维FFT结果
            max_index = np.argmax(angle_fft)                    # 找到空间维FFT的最大值下标
            theta_rad = spatial_theta_rad_axis[max_index]       # 由最大值下标，在空间轴中确定角度
            LOS_range = LOS_range_axis[cur_RD_index[0]]         # 由RD矩阵的(i,j)信息，找到LOS距离
            radial_distance = LOS_range / np.cos(theta_rad)     # 由LOS距离求出点到点的径向距离
            theta_distance_info.append([theta_rad, radial_distance])    # 记录距离-角度信息
            x_pos = radial_distance * np.sin(theta_rad)         # 求出x位置
            y_pos = radial_distance * np.cos(theta_rad)         # 求出y位置
            X_Y_info.append([x_pos, y_pos])                     # 记录X-Y信息
        theta_distance_info = np.array(theta_distance_info)
        X_Y_info = np.array(X_Y_info)
        self.__data_obj.update_theta_distance_info(theta_distance_info)
        self.__data_obj.update_X_Y_info(X_Y_info)

# #################################### 相关参数 ##########################################################
    def get_R_max(self):
        c = 3e8
        chirp_slope = self.__radar_para_obj.get_chirp_slope() * 1e12
        fast_time_Fs = self.__radar_para_obj.get_adc_sample_rate_in_kHz() * 1e3
        unit_R_beat_freq = 2 * chirp_slope / c
        R_max = (fast_time_Fs / 2) / unit_R_beat_freq
        return R_max

    def get_V_max(self):
        c = 3e8
        f0 = 77e9
        radar_lambda = c / f0
        chirp_time = (self.__radar_para_obj.get_chirp_rise_time() + self.__radar_para_obj.get_chirp_inter_time()) * 1e-6
        slow_time_Fs = 1 / chirp_time
        unit_V_doppler_freq = 2 / radar_lambda
        V_max = (slow_time_Fs / 2) / unit_V_doppler_freq
        return V_max

    def get_N_FFT_1(self):
        return self.__radar_para_obj.get_adc_sample_num()

    def get_N_FFT_2(self):
        return self.__radar_para_obj.get_chirps_in_frame()


