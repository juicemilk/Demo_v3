from signal_processing_function import SignalProcessing


class SignalProcessingManage():
    def __init__(self):
        self.__processing_frame_cnt = 0  # 进行了多少次处理
        self.signal_processing_obj = SignalProcessing()

    def get_handle(self, global_object):
        self.signal_processing_obj.get_handle(global_object)

    def radar_signal_process(self):
        """ 对一帧数据进行信号处理 """
        self.__processing_frame_cnt += 1
        self.signal_processing_obj.signal_processing_start()
