#if defined(ARDUINO_SAMD_FEATHER_M0) // Feather M0 w/Radio
#define RFM69_CS      8
#define RFM69_INT     3
#define RFM69_RST     4
#define LED           LED_BUILTIN
#endif

const int POWER = 12;

void setup() {
  Serial.begin(115200);
  // The Moisture sensor's v + is connected to the POWER GPIO pin.
  pinMode(POWER, OUTPUT);
}

void loop() {
  Serial.println("...getting moisture reading...");
  int moisture_reading = read_moisture();
  Serial.print("Moisture reading: ");
  Serial.println(moisture_reading);
  Serial.print("Battery level: ");
  Serial.println(read_battery_level());
 

}
int read_moisture() {

  // Average over nReadings.
  // turn the sensor on and wait a moment...
  digitalWrite(POWER, HIGH);
  delay(1000);
  const int num_readings = 10;
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
