import numpy as np
from datetime import datetime


class DataTrans():
    def __init__(self):
        self.__data_obj = None
        self.__radar_para_obj = None
        self.__signal_manage_obj = None
        self.__samples_in_chirp = None
        self.__chirps_in_frame = None
        self.__num_of_IQ_data_per_frame = None
        self.__complex_data_buffer = np.array([])
        self.__data_trans_cnt = 0     # 进行了多少次数据转换
        self.__frame_cnt = 0    # 进行了多少次数据处理

    def get_handle(self, global_object):
        self.__data_obj = global_object.data_obj
        self.__radar_para_obj = global_object.radar_para_obj
        self.__signal_manage_obj = global_object.signal_processing_manage_obj
        self.__samples_in_chirp = self.__radar_para_obj.get_samples_in_chirp()
        self.__chirps_in_frame = self.__radar_para_obj.get_chirps_in_frame()
        self.__num_of_IQ_data_per_frame = self.__samples_in_chirp * self.__chirps_in_frame * 4  # 4 channel

    def __complex_data_buffer_size(self):
        return len(self.__complex_data_buffer)

    def check_data_is_ready_to_process(self):
        """ 如果数据量达到一帧，就将这一帧的数据存好；否则继续进行数据转换 """
        if self.__complex_data_buffer_size() >= self.__num_of_IQ_data_per_frame:
            frame_data_length = self.__num_of_IQ_data_per_frame
            frame_data = self.__complex_data_buffer[:frame_data_length]
            self.__complex_data_buffer = self.__complex_data_buffer[frame_data_length:]
            self.__data_obj.put_one_frame_data_to_frame_buffer(frame_data)
            self.__frame_cnt += 1
            print('第' + str(self.__frame_cnt) + '帧传输完毕，当前时间' + str(datetime.now()))
            print('    Hex缓冲区大小:' + str(self.__data_obj.raw_hex_buffer_size()) + ', Complex缓冲区大小:' + str(self.__complex_data_buffer_size()))
        else:
            if not self.__data_obj.raw_hex_buffer_is_empty():
                self.__data_trans_cnt += 1
                self.__trans_data_from_hex_buffer_to_complex_buffer()

    def __trans_data_from_hex_buffer_to_complex_buffer(self):
        """ 从待处理的hex_stream中，将数据转存到complex_buffer中 """
        raw_hex_stream = self.__data_obj.get_one_package_from_hex_buffer()
        # 将raw_hex_stream的bytes数组转换为int16数组
        dt = np.int16
        int_stream = np.frombuffer(raw_hex_stream, dt)
        data_len = len(int_stream)
        # channel 0
        ch0_real = int_stream[0:data_len:8]
        ch0_imag = int_stream[4:data_len:8]
        ch0_IQ = ch0_real + 1j * ch0_imag
        # channel 1
        ch1_real = int_stream[1:data_len:8]
        ch1_imag = int_stream[5:data_len:8]
        ch1_IQ = ch1_real + 1j * ch1_imag
        # channel 2
        ch2_real = int_stream[2:data_len:8]
        ch2_imag = int_stream[6:data_len:8]
        ch2_IQ = ch2_real + 1j * ch2_imag
        # channel 3
        ch3_real = int_stream[3:data_len:8]
        ch3_imag = int_stream[7:data_len:8]
        ch3_IQ = ch3_real + 1j * ch3_imag
        # 合并输出
        merge_array = np.array([ch0_IQ, ch1_IQ, ch2_IQ, ch3_IQ])
        merge_array = merge_array.transpose()
        merge_array = merge_array.flatten()
        self.__complex_data_buffer = np.append(self.__complex_data_buffer, merge_array)
