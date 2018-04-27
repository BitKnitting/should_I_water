/*
 * Use to figure out where an error occured....
 */
 #ifdef LED_DEBUG
 #define BlinkFailInitRadio     {Blink(200,10);digitalWrite(LED,LOW);}
 #define BlinkFailPacketReceive {Blink(200,20);digitalWrite(LED,LOW);}
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
 #define BlinkFailInitRadio
 #define BlinkFailPacketReceive
 #endif
