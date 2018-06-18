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
#define BlinkAfterInitStuff    {Blink.blink(200,5);}
#define BlinkGotTime           {Blink.blink(200,10);}
#define BlinkGettingTime       {Blink.blink(100,1);}
#define BlinkSendingMoisture   {Blink.blink(200,5);}
#define BlinkGoToSleep         {Blink.blink(200,3);Blink.blink(300,3);Blink.blink(200,3);}
#define BlinkWakeUp            {Blink.blink(200,1);}
#define BlinkFailInitRadio     {Blink.blink(200,10);}
#define BlinkFailPacketReceive {Blink.blink(200,20);}
#define BlinkStartWatering {Blink.blink(300,3);Blink.blink(500,2);Blink.blink(300,3);}
#define BlinkStopWatering BlinkStartWatering
#define BlinkFinishedWatering BlinkStartWatering
#define BlinkReceivedMessage {Blink.blink(600,2);}
#define BlinkSentMessage {Blink.blink(200,5);}

class Blinks {
public:
  Blinks(bool debug=true);
  void                    blink(byte DELAY_MS, byte loops);
private:
  bool                    _debug;
};

#endif
