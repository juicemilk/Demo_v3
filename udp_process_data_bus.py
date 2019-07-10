from udp_process import UdpProcess
from udp_link_data_bus import UdpLinkDataBus


class UdpProcessDataBus(UdpProcess):
    def __init__(self):
        UdpProcess.__init__(self)
        udp_link_data_obj = UdpLinkDataBus()
        self.set_udp_link_obj(udp_link_data_obj)

    def get_handle(self, global_object):
        self.udp_link_obj.get_handle(global_object)
