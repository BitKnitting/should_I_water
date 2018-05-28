/********************************************************
 * GardenDataTypes.h
 * copyright - Margaret Johnson, 2018
 * If you use, please give credit.
 * The stuff in here is used by all pucks that are involved
 * with watering the garden.  
 * This include file is used by MoisturePuck_2018.ino and WateringPuck_2018.ino.
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
#define LED           LED_BUILTIN
#endif
// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

const uint8_t   _MOISTURE_INFO_PACKET            =   1;
const uint8_t   _MOISTURE_INFO_PACKET_RECEIVED   =   2;
const uint8_t   _TIME_INFO_PACKET                =   3;
const uint8_t   _TEST_PACKET                     =   4;
const uint8_t   _START_WATERING_PACKET           =   5; // Aligns with packet types identified in MoisturePuck_2018.
const uint8_t   _DONE_WATERING_PACKET            =   6;
const uint8_t   _BUSY_PACKET                     =   98;// Asked to water, but we're currently watering.
const uint8_t   _ERROR_IN_PACKET_RECEIVED        =   99;
const uint16_t  _TEST_VALUE                      =   0x1234;

/********************************************************************************
 * Note the use of __attribute__((packed)) ...I got this from the GCC documentation,
 * https://gcc.gnu.org/onlinedocs/gcc-4.0.4/gcc/Type-Attributes.html:
 * This attribute, attached to struct or union type definition, specifies that each 
 * member of the structure or union is placed to minimize the memory required.
 * This way, extra bytes don't get carried within the RFM69 packets...
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
} ;
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
  uint8_t watering_minutes;
};
const time_t MAX_WATERING_MINUTES = 30;
union wateringUnion_t
{
  wateringInfo_t values;
  uint8_t b[sizeof(wateringInfo_t)];
} wateringInfo;
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
