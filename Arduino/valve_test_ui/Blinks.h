/*
   Use to figure out where an error occured....
*/
#define LED           LED_BUILTIN
#ifdef LED_DEBUG
#define BlinkAfterInitStuf     {Blink(200,5);digitalWrite(LED,LOW);}
#define BlinkGotTime           {Blink(200,10);digitalWrite(LED,LOW);}
#define BlinkSendingMoisture   {Blink(200,5);digitalWrite(LED,LOW);}
#define BlinkGoToSleep         {Blink(200,5);digitalWrite(LED,LOW);}
#define BlinkWakeUp            {Blink(200,1);digitalWrite(LED,LOW);}
#define BlinkFailInitRadio     {Blink(200,10);digitalWrite(LED,LOW);}
#define BlinkFailPacketReceive {Blink(200,20);digitalWrite(LED,LOW);}
#define BlinkStartWatering {Blink(300,3);Blink(500,2);Blink(300,3);digitalWrite(LED,HIGH);}
#define BlinkStopWatering BlinkStartWatering
#define BlinkFinishedWatering BlinkStartWatering
#define BlinkReceivedMessage {Blink(400,6);digitalWrite(LED,HIGH);}

/********************************************************
  BLINK
********************************************************/
void Blink(byte DELAY_MS, byte loops) {
  for (byte i = 0; i < loops; i++)  {
    digitalWrite(LED, HIGH);
    delay(DELAY_MS);
    digitalWrite(LED, LOW);
    delay(DELAY_MS);
  }
}
/////////////////////////////////////////////////////////
#else
#define BlinkAfterInitStuf     
#define BlinkGotTime           
#define BlinkGoToSleep         
#define BlinkWakeUp            
#define BlinkFailInitRadio     
#define BlinkFailPacketReceive 
#define BlinkStartWatering 
#define BlinkStopWatering 
#define BlinkFinishedWatering 
#define BlinkReceivedMessage
#endif
