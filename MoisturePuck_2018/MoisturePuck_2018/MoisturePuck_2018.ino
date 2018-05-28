//
// MoisturePuck_2018 evolved my 2017 effort to at least initially support the 3 planters in the front
// of our house.  The assumption is there is a Rasp Pi server listening for either a time info or moisture
// packet.  I would have liked to write this firmware in CircuitPython.  I did not because CircuitPython
// does not support RTC on m0.  So for power management reasons, I'm using Arduino firmware.
//
// copyright (c)  Margaret Johnson
//////////////////////////////////////////////////////////////////////////////////////////////////////////
//#define DEBUG
#include <DebugLib.h>
#include <RTCZero.h>
RTCZero rtc;
#include "GardenDataTypes.h"
timeUnion_t timeInfo;
testUnion_t testPacket;
moistureUnion_t moistureInfo;
// LED is used in Blinks.h.
#define LED_DEBUG
#include "Blinks.h"
/************************************************
   The NODE_ID is Unique to each node.
 ************************************************/
 const uint8_t   _NODE_ID                         =   1;

const int NUMBER_OF_TRIES = 10;

const int POWER = 12;


bool bHaveTimeInfo = false;
int  num_test_packets_sent = 0;


/********************************************************
   setup
 ********************************************************/
void setup() {
  init_stuff();
}
/********************************************************
   loop
   After getting the time info, the chip goes to sleep.
   The chip wakes up when the watering hour happens.
 ********************************************************/
void loop() {
  // Send a few test packets to see if we're talking to the Rasp Pi...
  // The logfile on the Rasp Pi needs to be checked to see if it received
  // test packets.
  //  if (num_test_packets_sent < 2) {
  //    DEBUG_PRINTLNF("Sending test packet...");
  //    if (send_test_packet() ) {
  //      num_test_packets_sent += 1;
  //      DEBUG_PRINTLN(num_test_packets_sent);
  //    }
  //    delay(1000); // Put a delay in between sending packets...
  // Now that "a few" test packets have been sent, we need the current time and watering
  // hour from the Raspberry Pi..
  //  } else {
  if (!bHaveTimeInfo)  {
    DEBUG_PRINTLNF("Getting time info");
    get_time_info();
    //We're awake, which means we have time info...so take a moisture reading then
    //go back to sleep.
  } else {
    DEBUG_PRINTLNF("Sending moisture reading");
    send_moisture_reading();
    DEBUG_PRINTLNF("Going to sleep.");
    go_to_sleep();
  }
  //  }
}
/********************************************************
   send_test_packet()
 ********************************************************/
bool send_test_packet() {
  testPacket.values.packetType = _TEST_PACKET;
  testPacket.values.testValue = _TEST_VALUE;
  if (send_packet(testPacket.b, sizeof(testPacket))) {
    if (testPacket.values.packetType == _TEST_PACKET) {
      return true;
    }
  }
  return false;
}
/********************************************************
   get_time_info
 ********************************************************/
void get_time_info() {
  timeInfo.values.packetType = _TIME_INFO_PACKET;
  if (send_packet(timeInfo.b, sizeof(timeInfo))) {
    DEBUG_PRINTLN("***> Got a time info packet <***");
    bHaveTimeInfo = true;
    DEBUG_PRINTF("length of timeInfo: ");
    DEBUG_PRINTLN(sizeof(timeInfo.b));
    for (int i = 0; i < sizeof(timeInfo.b); i++) {
      DEBUG_PRINTLN(timeInfo.b[i]);
    }
    // Now that we have the time, let's set up the RTC and
    // an alarm to wake up...
    set_rtc();
    print_time_info();
  }
}
/********************************************************
   send_moisture_reading
 ********************************************************/
void send_moisture_reading() {
  moistureInfo.values.packetType = _MOISTURE_INFO_PACKET;
  get_reading();
  send_packet(moistureInfo.b, sizeof(moistureInfo));
}
/********************************************************************
   send_packet
 *******************************************************************/
bool send_packet(uint8_t *packet, uint8_t len) {
  DEBUG_PRINTF("Packet length: ");
  uint8_t buff[40];
  DEBUG_PRINTLN(len);
  for (int i = 0; i < NUMBER_OF_TRIES; i++) {
    rf69.send(packet, len);
    rf69.waitPacketSent();
    // Wait for a reply.
    // Waiting will block for up to 1/2 second.
    if (rf69.waitAvailableTimeout(500)) {
      // Message..hopefully...
      if (rf69.recv(packet, &len)) {
          DEBUG_PRINTLNF("Received a packet.");
          DEBUG_PRINTLN(len);
        if (packet[0] ==  _ERROR_IN_PACKET_RECEIVED) {
          DEBUG_PRINTLNF("!!! OOPS! Error in the packet we sent....");
          // Keep sending packets until the Rasp Pi can read it.
          // I'm assuming at most a few tries have been attempted.
        } else {

          return true;  // Let the caller interpret the contents of the packet.
        }
      }
    } else { // Timed out waiting for a response from the Rasp Pi.
      DEBUG_PRINTLNF("No reply from Rasp Pi...perhaps it is not running?");
    }
    delay(200);  //Give the radio a chance to "calm down..."
  }
  return false;
}
/********************************************************************
   get_reading
 *******************************************************************/
void get_reading() {
  moistureInfo.values.moistureReading = read_moisture();
  moistureInfo.values.batteryLevel = read_battery_level();
  DEBUG_PRINTF("Battery level: ");
  DEBUG_PRINTLN(moistureInfo.values.batteryLevel);
}
/********************************************************************
   read_moisture
   I assume readings will fluctuate, following a normal distribution.
   I take several readings over a given time and then send back the
   average.
 *******************************************************************/

int read_moisture() {
  digitalWrite(POWER, HIGH);
  delay(1000);
  // Average over nReadings.
  // turn the sensor on and wait a moment...
  const int num_readings = 30;
  // Take readings for a minute or so
  const int delay_between_readings = 10;
  float tot_readings = 0.;
  for (int i = 0; i < num_readings; i++) {
    int current_reading = analogRead(A0);  // !!!The moisture sensor must be on this analog pin.!!!
    tot_readings += current_reading;
    delay(delay_between_readings );
  }
  // Turn off power to the moisture sensor.
  digitalWrite(POWER, LOW);
  // Return an average of the values read.
  int reading = round(tot_readings / num_readings);
  DEBUG_PRINTF("Reading: ");
  DEBUG_PRINTLN(reading);
  return reading;

}
/********************************************************
   read_battery_level
  // Code from Adafruit's learn section:https://learn.adafruit.com/adafruit-feather-m0-radio-with-rfm69-packet-radio/overview?view=all#measuring-battery
********************************************************/
#define VBATPIN A7
float read_battery_level() {
  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage
  return (measuredvbat);
}
/********************************************************
  init_stuff
********************************************************/
void init_stuff() {
  // The Moisture sensor's v + is connected to the POWER GPIO pin.
  pinMode(POWER, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
  timeInfo.values.node_id = _NODE_ID;
  testPacket.values.node_id = _NODE_ID;
  moistureInfo.values.node_id = _NODE_ID;
  init_radio();
  init_rtc();
}
/********************************************************
  init_radio
********************************************************/
void init_radio() {
  if (!rf69.init()) {
    BlinkFailInitRadio;
    DEBUG_PRINTLNF("init failed");
  }
  // Our Feathers use 915MHz...
  if (!rf69.setFrequency(915.0)) {
    BlinkFailInitRadio;
    DEBUG_PRINTLNF("setFrequency failed");
  }
  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power with the
  // ishighpowermodule flag set like this:
  rf69.setTxPower(20, true);  // range from 14-20 for power, 2nd arg must be true for 69HCW

  // The encryption key has to be the same as the one in the server
  //  uint8_t key[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
  //                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
  //  rf69.setEncryptionKey(key);
}
/********************************************************
  init_rtc
********************************************************/
void init_rtc() {
  rtc.begin();
  rtc.attachInterrupt(wake_up);
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
  DEBUG_PRINTF("Hour: ");
  DEBUG_PRINTLN(timeInfo.values.hour);
  rtc.setTime(timeInfo.values.hour, timeInfo.values.minute, timeInfo.values.second);
  // Now that we have a time packet, we can set an alarm to fire when we should send a moisture info packet to the Controller.'
  print_rtc_time();

  rtc.setAlarmTime(timeInfo.values.wateringHour, 00, 00);
  rtc.enableAlarm(rtc.MATCH_HHMMSS);
  //rtc.enableAlarm(rtc.MATCH_SS);
}
/********************************************************
  print_rtc_time
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
/********************************************************
  go_to_sleep
********************************************************/
void go_to_sleep() {
  print_rtc_time();
  rf69.sleep();
  rtc.standbyMode();
}
/********************************************************
  wake_up - called back by rtc when an alarm goes off.
********************************************************/
void wake_up() {
  DEBUG_PRINTLN(F("\nI'm Awake!"));
  print_rtc_time();
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
