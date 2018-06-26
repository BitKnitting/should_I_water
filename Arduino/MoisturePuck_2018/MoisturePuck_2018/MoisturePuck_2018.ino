//
// MoisturePuck_2018 evolved my 2017 effort to at least initially support the 3 planters in the front
// of our house.  The assumption is there is a Rasp Pi server listening for either a time info or moisture
// packet.  I would have liked to write this firmware in CircuitPython.  I did not because CircuitPython
// does not support RTC on m0.  So for power management reasons, I'm using Arduino firmware.
//
// copyright (c)  Margaret Johnson
//////////////////////////////////////////////////////////////////////////////////////////////////////////
//********************DEBUG *********************************
//#define DEBUG
#include <DebugLib.h>
#include <Blinks_lib.h>
Blinks Blink = Blinks();
//******************** Backyard Gardening *******************
#include <GardenCommon_lib.h>

moistureUnion_t moistureInfo;

/************************************************
   The NODE_ID is Unique to each node.
 ************************************************/
const uint8_t   _NODE_ID                         =   1;

GardenCommon gc(_NODE_ID);


/********************************************************
   setup
 ********************************************************/
void setup() {
  DEBUG_BEGIN;
  DEBUG_WAIT;
  DEBUG_PRINTLNF("...initializing stuff...");
  error_t e = gc.init_stuff();
  if (e != 0) {
    DEBUG_PRINTF("Error on init_stuff.  Error number: ");
    DEBUG_PRINTLN(e);
    DEBUG_PRINTLNF("EXITING until init_stuff error is figured out.");
    exit(0);
  }
  DEBUG_PRINTLNF("---> successful setup ");
}

/********************************************************
   loop
   After getting the time info, the chip goes to sleep.
   The chip wakes up when the watering hour happens.
 ********************************************************/
void loop() {
  // First synchronize the RTC with the Rasp Pi's time.
  if (!gc.have_time_info) {
    DEBUG_PRINTLNF("---> Asking for time info packet");
    gc.get_time_info();
    // If we have set the time, we get a moisture reading
    // and send it to the Rasp Pi.
  } else if (!gc.have_sent_moisture_reading) {
    DEBUG_PRINTLNF("Sending moisture reading");
    gc.have_sent_moisture_reading = send_moisture_reading();
  } else {
#ifndef DEBUG:
    // We then go to sleep until the watering time provided
    // us when we got the time info packet.
    gc.go_to_sleep();
#endif
  }
}
/********************************************************
   send_moisture_reading
 ********************************************************/
bool send_moisture_reading() {
  moistureInfo.values.packetType = _MOISTURE_INFO_PACKET;
  moistureInfo.values.node_id = _NODE_ID;
  get_reading();
  //BlinkSendingMoisture
  return (gc.send_packet(moistureInfo.b, sizeof(moistureInfo)) );

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




