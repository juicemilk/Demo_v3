import multiprocessing


class UdpProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.udp_link_obj = None        # 进程包含一个udp链接
        self.__active_flag = multiprocessing.Value('B', 1)

    def set_udp_link_obj(self, udp_link_obj):
        self.udp_link_obj = udp_link_obj

    def run(self):
        self.udp_link_obj.open_local_port()
        while self.is_active():
            self.udp_link_obj.listen_to_client()
        self.udp_link_obj.close_local_port()

    def is_active(self):
        return self.__active_flag.value

    def shut_down_process(self):
        self.__active_flag.value = 0

    def send_hex_msg_to_client(self, hex_msg):
        self.udp_link_obj.send_hex_msg_to_client(hex_msg)
