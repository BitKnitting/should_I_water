from receive_packets_lib import ReceivePackets
import struct

class ReceiveMoisturePackets(ReceivePackets):
  def _receive_done(self,packet):
    super()._receive_done(packet)
    if self.packet_type == self._MOISTURE_INFO_PACKET:
        self.handle_logging.print_info("Received a _MOISTURE_INFO_PACKET from node {}.".format(self.node_id))
        try:
            # Take care to strip out the packet type and node id.
            measurement,battery_level = struct.unpack('=hf',packet[2:])
            battery_level = round(battery_level,2)
            self.callback(self.node_id,measurement,battery_level)
            packet_to_send = [self._MOISTURE_INFO_PACKET_RECEIVED]
        except struct.error as e:
            self.handle_logging.print_error(e)
            packet_to_send = [self._ERROR_IN_PACKET_RECEIVED]
