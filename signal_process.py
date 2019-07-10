import multiprocessing
from datetime import datetime
from signal_function import SignalFunc


class SignalProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.frame_cnt = 0
        self.signal_obj = SignalFunc()
        self.__data_obj = None
        self.__active_flag = multiprocessing.Value('B', 1)
        self.__ready_flag = multiprocessing.Value('B', 0)

    def get_handle(self, global_object):
        self.__data_obj = global_object.data_obj
        self.signal_obj.get_handle(global_object)

    def run(self):
        print('信号处理进程开始运行')
        while self.is_active():
            while self.__data_obj.frame_data_buffer_is_empty():
                continue
            self.frame_cnt += 1
            print('    开始进行第' + str(self.frame_cnt) + '次信号处理，当前时间' + str(datetime.now()))
            self.signal_obj.signal_processing_start()
            print('    处理完成，当前时间' + str(datetime.now()))
        print('信号处理进程结束')

    def is_active(self):
        return self.__active_flag.value

    def shut_down_process(self):
        self.__active_flag.value = 0
