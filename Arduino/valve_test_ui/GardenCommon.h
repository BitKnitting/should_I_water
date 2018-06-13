/********************************************************
   GardenCommon.h
   copyright - Margaret Johnson, 2018
   If you use, please give credit.
   Common datatypes, attributes, methods used across the pucks
   involved in watering our garden.

*/
//********************RFM69 stuff*********************************
#include <RH_RF69.h>
// RFM69 ID numbers
// Change to 434.0 or other frequency, must match RX's freq!
#define RF69_FREQ 915.0

#if defined(ARDUINO_SAMD_FEATHER_M0)
#define RFM69_CS      8
#define RFM69_INT     3
#define RFM69_RST     4
#endif
// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

#include <RTCZero.h>
RTCZero rtc;

const uint8_t   _MOISTURE_INFO_PACKET            =   1;

const uint8_t   _TIME_INFO_PACKET                =   3;
const uint8_t   _TEST_PACKET                     =   4;
const uint8_t   _START_WATERING_PACKET           =   5; // Aligns with packet types identified in MoisturePuck_2018.
const uint8_t   _DONE_WATERING_PACKET            =   6;
const uint8_t   _BUSY_PACKET                     =   98;// Asked to water, but we're currently watering.
const uint8_t   _ERROR_IN_PACKET_RECEIVED        =   99;
const uint16_t  _TEST_VALUE                      =   0x1234;

const int NUMBER_OF_TRIES = 10;
bool HaveTimeInfo = false;
/********************************************************************************
   Note the use of __attribute__((packed)) ...I got this from the GCC documentation,
   https://gcc.gnu.org/onlinedocs/gcc-4.0.4/gcc/Type-Attributes.html:
   This attribute, attached to struct or union type definition, specifies that each
   member of the structure or union is placed to minimize the memory required.
   This way, extra bytes don't get carried within the RFM69 packets...
*/

struct __attribute__((packed)) timeInfo_t
{
  uint8_t packetType;  // packetTime
  uint8_t node_id;
  uint8_t hour;
  uint8_t minute;
  uint8_t second;
  uint8_t wateringHour;
};
union timeUnion_t
{
  timeInfo_t values;
  uint8_t b[sizeof(timeInfo_t)];
} timeInfo;
/*********************************************************************************/
struct  __attribute__((packed)) testPacket_t
{
  uint8_t  packetType;
  uint8_t node_id;
  uint16_t testValue;
};
union testUnion_t
{
  testPacket_t values;
  uint8_t b[sizeof(testPacket_t)];
};

struct __attribute__((packed)) moistureInfo_t
{
  uint8_t packetType;
  // TBD: nodeID takes up 2 bytes for unpacking on the Rasp Pi side...
  uint8_t node_id;
  uint16_t     moistureReading;
  // Let the Rasp Pi know what the battery level is in case
  // it needs to be recharged.
  float   batteryLevel;
}; // Sends too many bytes unless use this....
union moistureUnion_t
{
  moistureInfo_t values;
  uint8_t b[sizeof(moistureInfo_t)];
} ;
//---------------------------------------------------------------------------
/*************************************************************************/
/* Watering Puck stuff
*/
struct __attribute__((packed)) wateringInfo_t // not sending battery info because plugged into 24VAC.
{
  uint8_t packet_type;
  uint8_t node_id;
  uint8_t valve_id;
  uint8_t watering_minutes;
};
const time_t MAX_WATERING_MINUTES = 30;
union wateringUnion_t
{
  wateringInfo_t values;
  uint8_t b[sizeof(wateringInfo_t)];
} ;
/*********************************************************************************/
// A control packet can be used any time we're sending a control message to the
// Raspberry pi.  So far this is "busy" and "done watering"
struct __attribute__((packed)) control_packet_t
{
  uint8_t packetType;
  uint8_t node_id;
};
union control_packet_Union_t
{
  control_packet_t values;
  uint8_t b[sizeof(control_packet_t)];
} control_packet;

uint8_t g_node_id;
/********************************************************
  init stuff
********************************************************/
void init_radio() {
  DEBUG_PRINTLNF("beginning of init_radio.");
  if (!rf69.init()) {
    DEBUG_PRINTLNF("init failed");
  }
  DEBUG_PRINTLNF("after init.");

  // Our Feathers use 915MHz...
  if (!rf69.setFrequency(915.0)) {
    DEBUG_PRINTLNF("setFrequency failed");
  }
  DEBUG_PRINTLNF("after set frequency.");

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power with the
  // ishighpowermodule flag set like this:
  rf69.setTxPower(20, true);  // range from 14-20 for power, 2nd arg must be true for 69HCW

  // The encryption key has to be the same as the one in the server
  //  uint8_t key[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
  //                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
  //  rf69.setEncryptionKey(key);
}
/********************************************************
  wake_up - called back by rtc when an alarm goes off.
********************************************************/
void wake_up() {
  DEBUG_PRINTLN(F("\nI'm Awake!"));
}
/********************************************************
  init_rtc
********************************************************/
void init_rtc() {
  rtc.begin();
  rtc.attachInterrupt(wake_up);
}
/********************************************************
  init_stuff
********************************************************/
void init_stuff(uint8_t node_id) {
  DEBUG_BEGIN;
  DEBUG_WAIT;
  DEBUG_PRINTLNF("...initializing stuff for a puck...");
  g_node_id = node_id;
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
  timeInfo.values.node_id = g_node_id;
  control_packet.values.node_id = g_node_id;
  init_radio();
  init_rtc();
  BlinkAfterInitStuf
}
/********************************************************
  debug print stuff
********************************************************/
void print_rtc_time() {
  DEBUG_PRINTF("rtc time: ");
  DEBUG_PRINT(rtc.getHours());
  DEBUG_PRINTF(":");
  DEBUG_PRINT(rtc.getMinutes());
  DEBUG_PRINTF(":");
  DEBUG_PRINTLN(rtc.getSeconds());
  DEBUG_PRINTF("Watering hour: ");
  DEBUG_PRINTLN(timeInfo.values.wateringHour);
}
/********************************************************************
   print_time_info
 *******************************************************************/
void print_time_info() {
  DEBUG_PRINTLN(F("\n**** Time Info*****"));
#ifdef DEBUG
  Serial.print(timeInfo.values.hour); Serial.print(F(":")); Serial.print(timeInfo.values.minute);
  Serial.print(F(":")); Serial.println(timeInfo.values.second);
  Serial.print(F("Watering hour: ")); Serial.println(timeInfo.values.wateringHour);
#endif
}
/********************************************************************
   print_bytes_in_hex
 *******************************************************************/
void print_bytes_in_hex(uint8_t *data, uint8_t length) {
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
  set_rtc
  see https://www.arduino.cc/en/Reference/RTC
********************************************************/
void set_rtc() {
  DEBUG_PRINTLNF("--->Setting RTC");
  // set the rtc library's time so the watering alarm time is correct.
  // ...well, approximately correct.  Given it will take several seconds from when the Rasp Pi sent
  // the packet...however, this amount of time won't make enough of a difference.
  rtc.setTime(timeInfo.values.hour, timeInfo.values.minute, timeInfo.values.second);
  // Now that we have a time packet, we can set an alarm to fire when we should send a moisture info packet to the Controller.'
  print_rtc_time();

  rtc.setAlarmTime(timeInfo.values.wateringHour, 00, 00);
  rtc.enableAlarm(rtc.MATCH_HHMMSS);
  //rtc.enableAlarm(rtc.MATCH_SS);
}

/********************************************************
  go_to_sleep
********************************************************/
void go_to_sleep() {
  print_rtc_time();
  rf69.sleep();
  rtc.standbyMode();
}
/********************************************************************
   recv_packet
 *******************************************************************/
bool recv_packet(uint8_t *packet, uint8_t len) {
  if (rf69.recv(packet, &len)) {
    DEBUG_PRINTLNF("Received a packet.");
    print_bytes_in_hex(packet, len);
    if (packet[1] != g_node_id) {
      DEBUG_PRINTF("---> packet for node ");
      DEBUG_PRINT(packet[1]);
      DEBUG_PRINTF(" this is node ");
      DEBUG_PRINTLN(g_node_id);
    } else if (packet[0] ==  _ERROR_IN_PACKET_RECEIVED) {
      DEBUG_PRINTLNF("!!! OOPS! Error in the packet we sent....");
      // Keep sending packets until the Rasp Pi can read it.
      // I'm assuming at most a few tries have been attempted.
    } else if ( (packet[0] == _TIME_INFO_PACKET) && HaveTimeInfo ) {
      DEBUG_PRINTLNF("...already have a time info packet...");
    } else {
      return true;  // Let the caller interpret the contents of the packet.
    }
  }
}
/********************************************************************
   send_packet
   We send a packet and then expect an acknowledgement.
 *******************************************************************/
bool send_packet(uint8_t *packet, uint8_t len) {
  uint8_t packet_type = packet[0];
  DEBUG_PRINTF("Packet type is ");
  DEBUG_PRINTLN(packet_type, HEX);
  for (int i = 0; i < NUMBER_OF_TRIES; i++) {
    DEBUG_PRINTLNF("Sending packet ");
    print_bytes_in_hex(packet, len);
    rf69.send(packet, len);
    rf69.waitPacketSent();
    // Wait for a reply.
    // Waiting will block for up to 1/2 second.
    if (rf69.waitAvailableTimeout(500)) {
      if (recv_packet(packet, len)) {
        if (packet[0] == packet_type) {
          DEBUG_PRINTLNF("...Received expected packet type.");
          return true;
        }
      }
    } else { // Timed out waiting for a response from the Rasp Pi.
      DEBUG_PRINTLNF("No reply from Rasp Pi...perhaps it is not running?");
    }
    delay(2000);  //Give the radio a chance to "calm down..."
  }
  return false;
}

/********************************************************************
  time_failed_check
*******************************************************************/
bool time_failed_check() {
  if ((timeInfo.values.hour == 0) && (timeInfo.values.minute == 0) && (timeInfo.values.minute == 0) ) {
    return true;
  }
  return false;
}
/********************************************************
   get_time_info()
 ********************************************************/
void get_time_info() {
  DEBUG_PRINTLNF("--> asking for a Time Info packet. ");
  timeInfo.values.packetType = _TIME_INFO_PACKET;
  if (send_packet(timeInfo.b, sizeof(timeInfo))) {
    DEBUG_PRINTLNF("***> Got a time info packet <***");
    DEBUG_PRINTF("Packet contents: ");
    print_bytes_in_hex(timeInfo.b, sizeof(timeInfo_t));
    if (time_failed_check()) {
      // Ask again for a time packet.
      return;
    }
    print_time_info();
    // Now that we have the time, let's set up the RTC and
    // an alarm to wake up...
    set_rtc();
    DEBUG_PRINTLNF("About to set have_time_info to TRUE");
    HaveTimeInfo = true;
    return;
  }
}
