/*
   Use to figure out where an error occured....
*/
#ifndef _BlinksLib_h
#define _BlinksLib_h

#include "Arduino.h"
#define LED           LED_BUILTIN
// NOTE: CREATE an instance of Blink like this:
// Blinks Blink = Blinks();
// Then these macros work.
#define BlinkAfterInitStuff             {Blink.blink(200,5);Blink.blink(100,5);}
// The Current Hour should be the hour returned in the time info packet.
#define BlinkGotTime(current_hour)      {Blink.blink(600,current_hour);}
// Show the hour the chip will wake up to take a reading.
#define BlinkAlarmSet(alarm_hour)       {Blink.blink(1000,alarm_hour);}
// TBD...#define BlinkGettingTime       {Blink.blink(100,1);}
#define BlinkGettingTime
#define BlinkSendingMoisture   {Blink.blink(100,10);}
#define BlinkGoToSleep         {Blink.blink(100,10);Blink.blink(300,3);Blink.blink(200,3);}
#define BlinkWokeUp            {Blink.blink(200,10);}
#define BlinkFailInitRadio     {Blink.blink(200,10);}
#define BlinkFailPacketReceive {Blink.blink(200,20);}
#define BlinkStartWatering {Blink.blink(300,3);Blink.blink(500,2);Blink.blink(300,3);}
#define BlinkStopWatering BlinkStartWatering
#define BlinkFinishedWatering BlinkStartWatering
#define BlinkReceivedMessage {Blink.blink(600,2);}
// TBD on blinking when a message is sent.
#define BlinkSentMessage


class Blinks {
public:
  Blinks(bool debug=true);
  void                    blink(uint16_t DELAY_MS, byte loops);
private:
  bool                    _debug;
};

#endif
