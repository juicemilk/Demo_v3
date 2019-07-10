from udp_link import UdpLink
import time


class UdpLinkControlBus(UdpLink):
    def __init__(self):
        UdpLink.__init__(self)
        self.udp_manage_obj = None
        self.data_trans_manage_obj = None
        host_ip = ('192.168.33.30', 4096)  # host addr
        client_ip = ('192.168.33.180', 4096)  # client addr
        self.set_ip_port(host_ip, client_ip)

    def get_handle(self, global_object):
        self.udp_manage_obj = global_object.udp_manage_obj
        self.data_trans_manage_obj = global_object.data_trans_manage_obj

    def listen_to_client(self):
        if self.recv_msg_flag():
            hex_stream = self.receive_msg
            str_msg = self.hex_stream_to_string(hex_stream).strip()
            print("receive: " + str_msg)
            if str_msg == '5A A5 0A 00 00 01 AA EE':
                # 收到采集板发来的采集数据完成消息，向采集板发送停止采集指令
                self.udp_manage_obj.send_stop_sample_command()
            if str_msg == '5A A5 06 00 00 00 AA EE':
                # 收到采集板停止采集的确认消息
                print('采集板已停止工作。')
                self.udp_manage_obj.shutdown_udp_process()
                # self.data_trans_manage_obj.shut_down_data_trans()

    def open_local_port(self):
        UdpLink.open_local_port(self)
        print('已建立控制总线UDP连接')

    def close_local_port(self):
        UdpLink.close_local_port(self)
        print('已关闭控制总线UDP连接')