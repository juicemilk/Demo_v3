from data_record import DataRecord
from radar_parameter import RadarParameter
from udp_manage import UdpManage
from signal_manage import SignalManage
from data_trans_manage import DataTransManage


class RadarAPI():
    def __init__(self):
        self.data_obj = DataRecord()
        self.radar_para_obj = RadarParameter()
        self.udp_manage_obj = UdpManage()
        self.signal_processing_manage_obj = SignalManage()
        self.data_trans_manage_obj = DataTransManage()
        self.udp_manage_obj.get_handle(self)
        self.data_trans_manage_obj.get_handle(self)
        self.signal_processing_manage_obj.get_handle(self)
        self.start_process()

    def start_process(self):
        self.udp_manage_obj.start_udp_process()
        self.data_trans_manage_obj.start_data_trans()
        self.signal_processing_manage_obj.start_signal_process()

    def shutdown_process(self):
        self.udp_manage_obj.shutdown_udp_process()
        self.data_trans_manage_obj.shut_down_data_trans()
        self.signal_processing_manage_obj.shut_down_signal_process()
