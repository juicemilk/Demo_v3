from udp_process_control_bus import UdpProcessControlBus
from udp_process_data_bus import UdpProcessDataBus


class UdpManage():
    """ UDP管理类，管理控制总线和数据总线 """
    def __init__(self):
        self.__udp_control_process_obj = UdpProcessControlBus()
        self.__udp_data_process_obj = UdpProcessDataBus()

    def get_handle(self, global_object):
        self.__udp_control_process_obj.get_handle(global_object)
        self.__udp_data_process_obj.get_handle(global_object)

    def start_udp_process(self):
        self.__udp_control_process_obj.start()
        self.__udp_data_process_obj.start()

    def shutdown_udp_process(self):
        self.__udp_control_process_obj.shut_down_process()
        self.__udp_data_process_obj.shut_down_process()

    def send_start_sample_command(self):
        hex_msg = b'\x5A\xA5\x05\x00\x00\x00\xAA\xEE'
        self.__udp_control_process_obj.send_hex_msg_to_client(hex_msg)
        print("send start sample command: 5A A5 05 00 00 00 AA EE")

    def send_stop_sample_command(self):
        hex_msg = b'\x5a\xa5\x06\x00\x00\x00\xaa\xee'
        self.__udp_control_process_obj.send_hex_msg_to_client(hex_msg)
        print('send stop sample command: 5A A5 06 00 00 00 AA EE')

