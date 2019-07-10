from udp_process import UdpProcess
from udp_link_control_bus import UdpLinkControlBus


class UdpProcessControlBus(UdpProcess):
    def __init__(self):
        UdpProcess.__init__(self)
        udp_link_control_obj = UdpLinkControlBus()
        self.set_udp_link_obj(udp_link_control_obj)

    def get_handle(self, global_object):
        self.udp_link_obj.get_handle(global_object)
