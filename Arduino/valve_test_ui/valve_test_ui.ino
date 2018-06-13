/*
   valve_test_ui

   UI side of testing the watering_puck code.  Input is which
   valve to turn on/off.  The valves I use are the ones in my
   backyard.  valve_test_ui is run on one feather.  It talks to
   the watering puck in my backyard.
*/
#define DEBUG
#define LED_DEBUG
#include <DebugLib.h>
#include <GardenCommon_lib.h>


GardenCommon gc(3);




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
  showHelp();
}

void loop() {
  serialHandler();

}
//***********************************************************
// RESPOND TO CHAR TYPED INTO SERIAL TERMINAL
//***********************************************************
void serialHandler() {

  char inChar;
  error_t e;
  if ((inChar = Serial.read()) > 0) {
    switch (inChar) {
      case 'y': // Turn on Yellow Valve
      case 'Y':
        DEBUG_PRINTLNF("\n-> Turning on the Yellow Valve");
        e = gc.send_control_packet(_YELLOW_VALVE_PACKET,4);
        DEBUG_PRINTLN(e);
        if (e != all_good) {
          DEBUG_PRINTLNF("could not send control packet.");
        }
        showHelp();
        break;

      case 'b': // Turn on Blue Valve
      case 'B':
        DEBUG_PRINTLNF("\n-> Turning on the Blue Valve");
        e = gc.send_control_packet(_BLUE_VALVE_PACKET,4);
        if (e != all_good) {
          DEBUG_PRINTLNF("could not send control packet.");
        }
        showHelp();
        break;
      case 'g': // Turn on Blue Valve
      case 'G':
        DEBUG_PRINTLNF("\n-> Turning on the Green Valve");
         gc.send_control_packet(_GREEN_VALVE_PACKET,4);
        if (e != all_good) {
          DEBUG_PRINTLNF("could not send control packet.");
        }

        showHelp();
        break;
      case '?':
      case 'h': // Display help
        showHelp();
      default:

        break;
    }
    //    if (control_packet.values.packetType != 0) {
    //      send_packet(control_packet.b, sizeof(control_packet));
    //    }
  }
}
//***********************************************************
// DISPLAY HELP
//***********************************************************
const char helpText[] PROGMEM =
  "\n"
  "Available commands : " "\n"
  "  ?     - shows available comands" "\n"
  "  y     - turn on the yellow valve" "\n"
  "  b     - turn on the blue valve" "\n"
  "  g     - turn on the green valve" "\n"
  ;
/*-----------------------------------------------------------
  show command line menu
  -----------------------------------------------------------*/
static void showHelp () {
  showString(helpText);
}
static void showString (PGM_P s) {
  for (;;) {
    char c = pgm_read_byte(s++);
    if (c == 0)
      break;
    if (c == '\n')
      Serial.print('\r');
    Serial.print(c);
  }
}
