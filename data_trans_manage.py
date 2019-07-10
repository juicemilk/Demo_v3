from data_trans_process import DataTransProcess


class DataTransManage():
    def __init__(self):
        self.__data_trans_process_obj = DataTransProcess()

    def get_handle(self, global_object):
        self.__data_trans_process_obj.get_handle(global_object)

    def start_data_trans(self):
        self.__data_trans_process_obj.start()

    def shut_down_data_trans(self):
        self.__data_trans_process_obj.shut_down_process()