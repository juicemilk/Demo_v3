import multiprocessing


class RadarParameter():
    def __init__(self):
        self.__carry_freq = multiprocessing.Value('I', 77)          # in GHz
        self.__chirp_slope = multiprocessing.Value('I', 15)         # in MHz/us
        self.__chirp_rise_time = multiprocessing.Value('I', 30)     # in us
        self.__chirp_inter_time = multiprocessing.Value('I', 10)   # in us
        self.__adc_sample_rate = multiprocessing.Value('I', 10)     # in MHz
        self.__adc_start_delay = multiprocessing.Value('I', 3)      # in us
        self.__samples_in_chirp = multiprocessing.Value('I', 128)     # num of points
        self.__chirps_in_frame = multiprocessing.Value('I', 64)    # num of points
        self.__N_FFT_1 = multiprocessing.Value('I', 128)
        self.__N_FFT_2 = multiprocessing.Value('I', 64)
        self.__frame_time = multiprocessing.Value('I', 50)          # in ms
        self.__num_of_frames = multiprocessing.Value('I', 256)     # num of points
        self.__is_T1R1_mode = multiprocessing.Value('I', 0)

    def set_chirp_slope(self, chirp_slope):
        self.__chirp_slope.value = chirp_slope

    def get_chirp_slope(self):
        return int(self.__chirp_slope.value)

    def set_chirp_rise_time(self, chirp_rise_time):
        self.__chirp_rise_time.value = chirp_rise_time

    def get_chirp_rise_time(self):
        return int(self.__chirp_rise_time.value)

    def set_chirp_inter_time(self, chirp_inter_time):
        self.__chirp_inter_time.value = chirp_inter_time

    def get_chirp_inter_time(self):
        return int(self.__chirp_inter_time.value)

    def set_adc_sample_rate_in_MHz(self, adc_sample_rate):
        self.__adc_sample_rate.value = adc_sample_rate

    def get_adc_sample_rate_in_kHz(self):
        return int(self.__adc_sample_rate.value * 1000)

    def set_adc_start_delay(self, adc_start_delay):
        self.__adc_start_delay.value = adc_start_delay

    def get_adc_start_delay(self):
        return int(self.__adc_start_delay.value)

    def set_samples_in_chirp(self, adc_sample_num):
        self.__samples_in_chirp.value = adc_sample_num

    def get_samples_in_chirp(self):
        return int(self.__samples_in_chirp.value)

    def set_chirps_in_frame(self, chirps_in_frame):
        self.__chirps_in_frame.value = chirps_in_frame

    def get_chirps_in_frame(self):
        return int(self.__chirps_in_frame.value)

    def set_N_FFT_1(self, N_FFT_1):
        self.__N_FFT_1.value = N_FFT_1

    def get_N_FFT_1(self):
        return int(self.__N_FFT_1.value)

    def set_N_FFT_2(self, N_FFT_2):
        self.__N_FFT_2.value = N_FFT_2

    def get_N_FFT_2(self):
        return int(self.__N_FFT_2.value)

    def set_frame_time(self, frame_time):
        self.__frame_time.value = frame_time

    def get_frame_time(self):
        return int(self.__frame_time.value)

    def set_num_of_frames(self, num_of_frames):
        self.__num_of_frames.value = num_of_frames

    def get_num_of_frames(self):
        return int(self.__num_of_frames.value)

    def set_antenna_mode(self, flag):
        """ True表示一发一收，False表示两发四收 """
        self.__is_T1R1_mode.value = flag

    def is_T1R1_mode(self):
        return self.__is_T1R1_mode.value

    def get_R_gap(self):
        """ 距离门之间的间隔 """
        unit_R_beat_freq = 2e4 * self.get_chirp_slope() / 3
        Fs = self.get_adc_sample_rate_in_kHz() * 1e3
        R_gap = Fs / unit_R_beat_freq / self.get_N_FFT_1()
        return R_gap

    def get_V_gap(self):
        """ 速度门之间的间隔 """
        chirp_time = self.get_chirp_rise_time() + self.get_chirp_inter_time()
        chirp_time = chirp_time * 1e-6
        unit_V_doppler_freq = 513.33
        V_gap = 1/ chirp_time / unit_V_doppler_freq / self.get_N_FFT_2()
        return V_gap

    def get_R_max(self):
        c = 3e8
        chirp_slope = self.get_chirp_slope() * 1e12
        fast_time_Fs = self.get_adc_sample_rate_in_kHz() * 1e3
        unit_R_beat_freq = 2 * chirp_slope / c
        R_max = (fast_time_Fs / 2) / unit_R_beat_freq
        return R_max

    def get_V_max(self):
        c = 3e8
        f0 = 77e9
        radar_lambda = c / f0
        chirp_time = (self.get_chirp_rise_time() + self.get_chirp_inter_time()) * 1e-6
        slow_time_Fs = 1 / chirp_time
        unit_V_doppler_freq = 2 / radar_lambda
        V_max = (slow_time_Fs / 2) / unit_V_doppler_freq
        return V_max

    def get_BW_in_MHz(self):
        sample_time = self.get_samples_in_chirp() / (self.get_adc_sample_rate_in_kHz() * 1e3)
        BW = sample_time * self.get_chirp_slope() * 1e12
        return BW/1e6


if __name__ == '__main__':
    radar_para = RadarParameter()
    print('当前雷达参数：')
    msg = '最大可测距离 = ' + str(radar_para.get_R_max()) + '米'
    print(msg)
    msg = '距离分辨率 = ' + str(radar_para.get_R_gap()) + '米'
    print(msg)
    msg = '最大可测速度 = ' + str(radar_para.get_V_max()) + '米/秒'
    print(msg)
    msg = '速度分辨率 = ' + str(radar_para.get_V_gap()) + '米/秒'
    print(msg)
