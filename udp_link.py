""" 包含udp的收发相关函数 """
import socket


class UdpLink():
    def __init__(self):
        self.host_ip_port = None
        self.client_ip_port = None
        self.buf_size = 2048
        self.receive_client_ip_port = 0        # 收到消息的ip和端口
        self.host = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp协议
        self.receive_msg = b''     # received msg 初始化为空
        self.host.settimeout(0.001)       # 设置接收超时时间（秒）
        self.__package_cnt = 0  # 当前总共收到了多少个UDP数据包

    def set_ip_port(self, host_ip, client_ip):
        self.host_ip_port = host_ip
        self.client_ip_port = client_ip

    def open_local_port(self):
        self.host.bind(self.host_ip_port)   # 为host对象绑定ip地址，即打开网口

    def close_local_port(self):
        self.host.close()

    def listen_to_client(self):
        """ 虚函数，由子类重写 """
        return

    def recv_msg_flag(self):
        """ received new msg flag """
        try:
            self.receive_msg, self.receive_client_ip_port = self.host.recvfrom(self.buf_size)
        except Exception:   # 接收超时
            return False
        else:
            return True

    def hex_stream_to_string(self, hex_stream):
        """ 将一个hex比特流转为字符串形式 """
        str_msg = ''
        for byte_data in hex_stream:
            if byte_data < 16:
                str_msg = str_msg + '0' + (hex(byte_data)[2:]).upper() + ' '
            else:
                str_msg = str_msg + (hex(byte_data)[2:]).upper() + ' '
        return str_msg

    def send_hex_msg_to_client(self, hex_msg):
        """ send hex stream to client """
        self.host.sendto(hex_msg, self.client_ip_port)

    def increase_package_cnt_once(self):
        """ package_cnt是收到多少数据包的计数，增加一次计数 """
        self.__package_cnt += 1

    def package_cnt(self):
        """ package_cnt是收到多少数据包的计数 """
        return int(self.__package_cnt)
