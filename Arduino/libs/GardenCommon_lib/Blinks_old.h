/*
   Use to figure out where an error occured....
*/
#ifndef _BlinksLib_h
#define _BlinksLib_h
#include "Arduino.h"
#define LED           LED_BUILTIN
#define BlinkAfterInitStuff    {Blink(200,5);}
#define BlinkGotTime           {Blink(200,10);}
#define BlinkSendingMoisture   {Blink(200,5);}
#define BlinkGoToSleep         {Blink(200,5);}
#define BlinkWakeUp            {Blink(200,1);}
#define BlinkFailInitRadio     {Blink(200,10);}
#define BlinkFailPacketReceive {Blink(200,20);}
#define BlinkStartWatering {Blink(300,3);Blink(500,2);Blink(300,3);}
#define BlinkStopWatering BlinkStartWatering
#define BlinkFinishedWatering BlinkStartWatering
#define BlinkReceivedMessage {Blink(400,6);}
#define BlinkSentMessage {Blink(300,20);}

class Blinks {
public:
  Blinks(bool debug);
  void                    blink(byte DELAY_MS, byte loops);
};
#endif
