from signal_process import SignalProcess


class SignalManage():
    def __init__(self):
        self.signal_process_obj = SignalProcess()

    def get_handle(self, global_object):
        self.signal_process_obj.get_handle(global_object)

    def start_signal_process(self):
        """ 对一帧数据进行信号处理 """
        self.signal_process_obj.start()

    def shut_down_signal_process(self):
        self.signal_process_obj.shut_down_process()
