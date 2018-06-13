
#include <Arduino.h>
#include "GardenCommon_lib.h"
//#define DEBUG
#include <DebugLib.h>



// Thank you Nick Gammon: https://forum.arduino.cc/index.php?topic=409237.0
// In this Q&A Nick explains how to use object instances within a class.
// This helped me to figure out using rf69 as a class variable which is an
// instance of RH_RF69 class.
GardenCommon::GardenCommon(uint8_t node_id) : rf69(RFM69_CS, RFM69_INT), Blink()
{
  _node_id = node_id;
  have_time_info = false;
}
/********************************************************
  init_stuff
********************************************************/
error_t GardenCommon::init_stuff() {

    DEBUG_PRINTLNF("-->in init_stuff");
    timeInfo.values.node_id = _node_id;
    control_packet.values.node_id = _node_id;
    // The Moisture sensor's v + is connected to the POWER GPIO pin.
    pinMode(POWER, OUTPUT);
    error_t res_code = _init_radio();
    DEBUG_PRINTLNF("...after _init_radio");
    if (res_code != all_good) {
      return res_code;
    }
    _init_rtc();
    BlinkAfterInitStuff
    return all_good;
}
/********************************************************
  init radio
********************************************************/
error_t GardenCommon::_init_radio() {
  DEBUG_PRINTLNF("--> starting _init_radio");
  if (!rf69.init()) {
    DEBUG_PRINTLNF("init() of rf69 failed.");
    return (init_rf69_failed);
  }
  // Our Feathers use 915MHz...
  if (!rf69.setFrequency(915.0)) {
    DEBUG_PRINTLNF("setFrequency() of rf69 failed.");
    return init_rf69_freq_failed;
  }

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power with the
  // ishighpowermodule flag set like this:
  rf69.setTxPower(20, true);  // range from 14-20 for power, 2nd arg must be true for 69HCW

  // The encryption key has to be the same as the one in the server
  //  uint8_t key[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
  //                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
  //  rf69.setEncryptionKey(key);
  return all_good;
}
/********************************************************
  go_to_sleep
********************************************************/
void GardenCommon::go_to_sleep() {
  BlinkGoToSleep
  print_rtc_time();
  rf69.sleep();
  rtc.standbyMode();
}
/********************************************************
  wake_up - called back by rtc when it's alarm goes off.
********************************************************/
void wake_up() {
  DEBUG_PRINTLNF("I AM AWAKE!");
}
/********************************************************
  init_rtc
********************************************************/
void GardenCommon::_init_rtc() {
  rtc.begin();
  rtc.attachInterrupt(wake_up);
}
/********************************************************
   get_time_info()
 ********************************************************/
void GardenCommon::get_time_info() {
  timeInfo.values.packetType = _TIME_INFO_PACKET;
  int num_tries = 0;
  while (!have_time_info && num_tries++ < NUMBER_OF_TRIES) {
    BlinkGettingTime
    if (send_packet(timeInfo.b, sizeof(timeInfo))) {
      if (_time_passed_check() ){
        have_time_info = true;
      }
    }
  }
  if (have_time_info) {
    BlinkGotTime
    _set_rtc();
  }
}
/********************************************************************
  _time_passed_check
*******************************************************************/
bool GardenCommon::_time_passed_check() {
  if ((timeInfo.values.hour == 0) && (timeInfo.values.minute == 0) && (timeInfo.values.minute == 0) ) {
    return false;
  }
  return true;
}
/*******************************************************
  _set_rtc
  see https://www.arduino.cc/en/Reference/RTC
********************************************************/
void GardenCommon::_set_rtc() {
  // set the rtc library's time so the watering alarm time is correct.
  // ...well, approximately correct.  Given it will take several seconds from when the Rasp Pi sent
  // the packet...however, this amount of time won't make enough of a difference.
  rtc.setTime(timeInfo.values.hour, timeInfo.values.minute, timeInfo.values.second);
  // To conserve power, we'll put the chips to sleep when we don't need to access them.
  // The alarm wakes us up so we can either listen for or send packets.
  rtc.setAlarmTime(timeInfo.values.wateringHour, 00, 00);
  rtc.enableAlarm(rtc.MATCH_HHMMSS);
}
/********************************************************************
   watering_window
   The watering window is a 3 hour time frame that starts at the
   watering hour.
 *******************************************************************/
bool GardenCommon::is_in_watering_window() {
  uint8_t beginning_watering_hour = timeInfo.values.wateringHour;
  uint8_t end_watering_hour = beginning_watering_hour + 3;
  uint8_t current_hour = rtc.getHours();
  //Adjust to 24 hour clock.
  if (end_watering_hour > 23) {
    current_hour += 24;
  }
  if ((current_hour >= beginning_watering_hour) && (current_hour) <= end_watering_hour) {
    return true;
  }
  return false;
}
/********************************************************************
   recv_packet
 *******************************************************************/
bool GardenCommon::recv_packet(uint8_t *packet, uint8_t len) {
  if (rf69.recv(packet, &len)) {
    DEBUG_PRINTF(" Received packet: ");
    print_bytes_in_hex(packet,len);
    if (packet[1] != _node_id) {
        return false;
    } else if (packet[0] ==  _ERROR_IN_PACKET_RECEIVED) {
        return false;
    } else if ( (packet[0] == _TIME_INFO_PACKET) && have_time_info ) {
        return false; // Have already received a time info packet.
    } else {
      return true;  // Let the caller interpret the contents of the packet.
    }
  }
}
/********************************************************************
   send_packet
   We send a packet and then expect an acknowledgement.
 *******************************************************************/
bool GardenCommon:: send_packet(uint8_t *packet, uint8_t len) {
  uint8_t packet_type = packet[0];
  DEBUG_PRINTF(" Sent packet: ");
  print_bytes_in_hex(packet,len);
  rf69.send(packet, len);
  for (int i = 0; i < NUMBER_OF_TRIES; i++) {

    rf69.waitPacketSent();
    // Wait for a reply.
    // Waiting will block for up to 1/2 second.
    if (rf69.waitAvailableTimeout(500)) {
      if (recv_packet(packet, len)) {
        if (packet[0] == packet_type) {
          return true;
        }
      }
    }
    delay(2000);  //Give the radio a chance to "calm down..."
  }
  return false;
}
/********************************************************************
   recv_watering_packet
   -> Tell the watering puck which valve to turn on (i.e.: Start)
   -> Tell which valve to turn off (i.e.: Stop)
 *******************************************************************/
bool GardenCommon::recv_watering_packet() {
    if (recv_packet(wateringInfo.b, sizeof(wateringInfo_t)) ) {
      // Set the current state to either just received a start watering
      // or stop watering packet.
      packet_type = wateringInfo.values.packet_type;
      if (IS_VALVE(wateringInfo.values.valve_id) && wateringInfo.values.node_id == _node_id) {
        if (packet_type == _START_WATERING_PACKET) {
          // Send back a packet so the sender knows we got the watering packet.
          BlinkStartWatering
          valve_id = wateringInfo.values.valve_id;
          watering_minutes = wateringInfo.values.watering_minutes;
          return true;
        } else if (packet_type == _STOP_WATERING_PACKET) {
          BlinkStopWatering
          return true;
      }
    }
    // In any case, the Rasp Pi expects a response.
    rf69.send(wateringInfo.b,sizeof(wateringInfo.b));
    return false;
  }
}

/********************************************************************
   send_control_packet
 *******************************************************************/
error_t GardenCommon::send_control_packet(uint8_t command,uint8_t node_id) {
  control_packet.values.packet_type = command;
  control_packet.values.node_id = node_id;
  if (send_packet(control_packet.b,sizeof(control_packet_t)) ) {
    return all_good;
  }
  return send_packet_failed;

}

void GardenCommon::reply_with_control_packet(uint8_t packet_type,uint8_t node_id) {
  control_packet.values.node_id = node_id;
  control_packet.values.packet_type = packet_type;
  rf69.send(control_packet.b,sizeof(control_packet.b));
}
/********************************************************************
   print_bytes_in_hex
 *******************************************************************/
void GardenCommon::print_bytes_in_hex(uint8_t *data, uint8_t length) {
#ifdef DEBUG
  char tmp[6];
  for (int i = 0; i < length; i++) {
    sprintf(tmp, "0x%.2X", data[i]);
    DEBUG_PRINT(tmp); DEBUG_PRINT(" ");
  }
  DEBUG_PRINTLNF(" ");
#endif
}
/********************************************************
  print_rtc_time
********************************************************/
void GardenCommon::print_rtc_time() {
  DEBUG_PRINTF("rtc time: ");
  DEBUG_PRINT(rtc.getHours());
  DEBUG_PRINTF(":");
  DEBUG_PRINT(rtc.getMinutes());
  DEBUG_PRINTF(":");
  DEBUG_PRINTLN(rtc.getSeconds());
  DEBUG_PRINTF("Watering hour: ");
  DEBUG_PRINTLN(timeInfo.values.wateringHour);
}
