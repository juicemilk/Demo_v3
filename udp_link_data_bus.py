from udp_link import UdpLink


class UdpLinkDataBus(UdpLink):
    def __init__(self):
        UdpLink.__init__(self)
        self.radar_data_obj = None
        host_ip = ('192.168.33.30', 4098)  # host addr
        client_ip = ('192.168.33.180', 1024)  # client addr
        self.set_ip_port(host_ip, client_ip)

    def get_handle(self, global_object):
        self.radar_data_obj = global_object.data_obj

    def listen_to_client(self):
        if self.recv_msg_flag():
            hex_stream = self.receive_msg
            # 在传输数据模式中，只记录到内存中
            self.increase_package_cnt_once()
            self.radar_data_obj.put_into_raw_hex_buffer(hex_stream[10:])
            # print('收到了第' + str(self.package_cnt()) + '个数据包')

    def open_local_port(self):
        UdpLink.open_local_port(self)
        print('已建立数据总线UDP连接')

    def close_local_port(self):
        UdpLink.close_local_port(self)
        print('已关闭数据总线UDP连接')