/********************************************************
   GardenCommon.h
   copyright - Margaret Johnson, 2018
   If you use, please give credit.
   Common datatypes, attributes, methods used across the pucks
   involved in watering our garden.

*/
//********************RFM69 stuff*********************************
#ifndef _GardenCommon_h
#define _GardenCommon_h
#include "Arduino.h"
#include "GardenCommon_shared_properties.h"
// These properties are defined in GardenCommon_shared_properties.h


class GardenCommon {
public:
  GardenCommon(uint8_t node_id);
  error_t                 init_stuff();
  void                    get_time_info();
  bool                    have_time_info;
  uint8_t                 packet_type;
  uint8_t                 valve_id;
  uint8_t                 watering_minutes;
  bool                    is_in_watering_window();
  bool                    recv_packet(uint8_t *packet, uint8_t len);
  bool                    recv_watering_packet();
  bool                    send_packet(uint8_t *packet, uint8_t len);
  error_t                 send_control_packet(uint8_t command, uint8_t node_id);
  void                    reply_with_control_packet(uint8_t packet_type,uint8_t node_id);
  void                    go_to_sleep();
  void                    print_bytes_in_hex(uint8_t *data, uint8_t length);
  void                    print_rtc_time();
private:
  uint8_t                 _node_id;
  RH_RF69                 rf69;
  RTCZero                 rtc;
  Blinks                  Blink;
  timeUnion_t             timeInfo;
  control_packet_Union_t  control_packet;
  wateringInfoUnion_t     wateringInfo;
  error_t                 _init_radio();
  void                    _init_rtc();
  bool                    _time_passed_check();
  void                    _set_rtc();

};

#endif
