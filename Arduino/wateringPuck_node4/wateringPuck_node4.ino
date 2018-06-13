/*
   A Watering puck controls opening and closing valves at the
   request of a Rasp Pi server.

   I want stuff to be running "as low power as possible." So
   I set it up such that it is on at the time it expects a
   watering request from the Rasp Pi and then + 3 hours in case
   watering should be stopped/started outside of normal watering
   times.
*/
//********************DEBUG *********************************
//#define DEBUG
#include <DebugLib.h>
//******************** Backyard Gardening *******************
#include <GardenCommon_lib.h>
#include "Valve.h"
/*
   The unique number we've assigned to this (backyard) water puck.
*/
#define _NODE_ID        4


GardenCommon gc(_NODE_ID);
/*
   The water puck controls three valves.  I've labeled each valve with a color.
*/

Valve  yellow_valve = Valve(yellow_gpio);
Valve  blue_valve   = Valve(blue_gpio);
Valve  green_valve  = Valve(green_gpio);

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
uint8_t cnt = 0;
void loop() {
  // We want to sync with the Rasp Pi's time so that we will be
  // awake when expecting a packet.s
  if (!gc.have_time_info) {
    DEBUG_PRINTLNF("---> Asking for time info packet");
    gc.get_time_info();
  } else if (!gc.is_in_watering_window()) { // Is it currently within the watering window?  If not,
    // go to sleep.
    if (cnt > 20) {
      cnt = 0;
      DEBUG_PRINTLNF("");
    } else {
      cnt += 1;
      DEBUG_PRINTF(".");
    }
#ifndef DEBUG:  // don't go to sleep if debugging with serial console.
    // If we are awake, it means we are between the watering hour (typically 4 AM)
    // and + 3 hours (typically 7AM).  If it is after +3 hours, go to sleep.  The
    // rtc alarm will wake up up at the watering hour.
    gc.go_to_sleep();
#endif
  } else {
    // Check if we received a start or stop watering packet.
    // the timer library works by running the update() method in the loop.
    t.update();
    if ( gc.recv_watering_packet()) {
      handle_watering_packet();
    }
  }
}
/*****************************************************
   start_watering
******************************************************/

void handle_watering_packet() {
  switch (gc.valve_id) {
    case _YELLOW_VALVE:
      DEBUG_PRINTF("-->Told yellow valve to ");
      if (gc.packet_type == _START_WATERING_PACKET) {
        DEBUG_PRINTLNF("start watering.");
        yellow_valve.start_watering(yellow_valve_done_watering, gc.watering_minutes);
      }
      else if (gc.packet_type == _STOP_WATERING_PACKET) {
        DEBUG_PRINTLNF("stop watering.");
        yellow_valve.stop_watering();
      }
      break;
    case _BLUE_VALVE:
      DEBUG_PRINTF("-->Told blue valve to ");
      if (gc.packet_type == _START_WATERING_PACKET) {
        DEBUG_PRINTLNF("start watering.");
        blue_valve.start_watering(blue_valve_done_watering, gc.watering_minutes);
      }
      else if (gc.packet_type == _STOP_WATERING_PACKET) {
        DEBUG_PRINTLNF("stop watering.");
        blue_valve.stop_watering();
      }
      break;

    case _GREEN_VALVE:
      DEBUG_PRINTF("-->Told green valve to ");
      if (gc.packet_type == _START_WATERING_PACKET) {
        DEBUG_PRINTLNF("start watering.");
        green_valve.start_watering(green_valve_done_watering, gc.watering_minutes);
      }
      else if (gc.packet_type == _STOP_WATERING_PACKET) {
        DEBUG_PRINTLNF("stop watering.");
        green_valve.stop_watering();
      }
      break;
  }
}
/*****************************************************
   done_watering - callback from the Valve instance
   The callback is set up through the start_watering
   method.  Note: done is different than stop.  Stop means
   the Rasp Pi issued a stop watering command.  Done means
   the timer fired after the number of watering minutes completed.
******************************************************/
void yellow_valve_done_watering() {
  yellow_valve.stop_watering();
  DEBUG_PRINTLNF("Yellow valve is done watering.");
}
void blue_valve_done_watering() {
  blue_valve.stop_watering();
  DEBUG_PRINTLNF("Blue valve is done watering.");
}
void green_valve_done_watering() {
  green_valve.stop_watering();
  DEBUG_PRINTLNF("Green valve is done watering.");
}

