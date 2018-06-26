
// Use the built in red led to blink as an indication of what the
// firmware is doing when there is no debug output.

#include <Blinks_lib.h>

Blinks::Blinks(bool debug)
{
  _debug = debug;
  if (_debug){
    pinMode(LED, OUTPUT);
  }
}
/********************************************************
  BLINK
********************************************************/
void Blinks::blink(uint16_t DELAY_MS, byte loops) {
  if (_debug){
    for (byte i = 0; i < loops; i++)  {
      digitalWrite(LED, HIGH);
      delay(DELAY_MS);
      digitalWrite(LED, LOW);
      delay(DELAY_MS);
    }
  }
}
