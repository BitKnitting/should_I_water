from RFM69_lib import RFM69


class RFM69Messages:
    def __init__(self):
        super().__init__()
        self._MOISTURE_INFO_PACKET            =   1

        self._TIME_INFO_PACKET                =   3
        self._TEST_PACKET                     =   4
        self._START_WATERING_PACKET           =   5
        self._STOP_WATERING_PACKET            =   6
        self._WATERING_PACKET_RECEIVED        =   7
        self._NO_PACKET_TYPE                  =   100
        self._ERROR_IN_PACKET_RECEIVED        =   99
        self._TEST_VALUE                      =   0x1234
        ###################################################
        self.radio =  RFM69()
        self.set_of_packet_types = {self._MOISTURE_INFO_PACKET,
        self._TIME_INFO_PACKET,self._TEST_PACKET,self._START_WATERING_PACKET,
        self._WATERING_PACKET_RECEIVED, self._ERROR_IN_PACKET_RECEIVED}
