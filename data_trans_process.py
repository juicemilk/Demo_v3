import multiprocessing
from data_trans_function import DataTrans


class DataTransProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.__data_trans_obj = DataTrans()
        self.__active_flag = multiprocessing.Value('B', 1)

    def get_handle(self, global_obj):
        self.__data_trans_obj.get_handle(global_obj)

    def run(self):
        print('读取数据进程开始运行')
        while self.is_active():
            self.__data_trans_obj.check_data_is_ready_to_process()
        print('读取数据进程结束')

    def is_active(self):
        return self.__active_flag.value

    def shut_down_process(self):
        self.__active_flag.value = 0