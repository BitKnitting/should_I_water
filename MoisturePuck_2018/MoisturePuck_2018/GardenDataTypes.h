/********************************************************
 * GardenDataTypes.h
 * copyright - Margaret Johnson, 2018
 * If you use, please give credit.
 * The stuff in here is used by all pucks that are involved
 * with watering the garden.  So far this is the moisture and
 * water puck.
 */

const uint8_t   _MOISTURE_INFO_PACKET            =   1;
const uint8_t   _MOISTURE_INFO_PACKET_RECEIVED   =   2;
const uint8_t   _TIME_INFO_PACKET                =   3;
const uint8_t   _TEST_PACKET                     =   4;
const uint8_t   _ERROR_IN_PACKET_RECEIVED        =   99;
const uint8_t   _NODE_ID                         =   1;
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
