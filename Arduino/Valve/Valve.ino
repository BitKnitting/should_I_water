const uint8_t yellow_relay = 12;
const uint8_t blue_relay = 11;
const uint8_t green_relay = 6;

#include <LinkedList.h>

// The Valve class helps us control one of the valves to turn on/off for watering plants.
class Valve
{
  public:
    enum states
    {
      UNKNOWN,
      ON,
      OFF
    } state;
    uint8_t id;
    uint8_t minutes_on;
    int     timer_id;

    Valve(uint8_t gpio_pin, uint8_t watering_minutes)
    {
      state = UNKNOWN;
      id = gpio_pin;
      minutes_on = watering_minutes;
      pinMode(id, OUTPUT);
    }
    void start_watering() {
      // Turn on GPIO
      digitalWrite(id,HIGH);
      // Turn on Timer
      state = ON;

    }
    void stop_watering() {
      // Turn off GPIO
      // Turn off Timer
      state = OFF;
    }
};
LinkedList<Valve *>valveList = LinkedList<Valve *>();
void setup() {
  Serial.begin(115200);
  while (!Serial) {}
  //create a valve
  Valve v = Valve(1, 1, 20);
  valveList.add(&v);
  // create another valve
  Valve another_valve = Valve(2, 3, 15);
  Valve one_more_valve = Valve(3, 3, 30);
  valveList.add(&one_more_valve);
  // add to list
  valveList.add(&another_valve);
  Serial.print("There are ");
  Serial.print(valveList.size());
  Serial.println(" valves.");

  for (int i = 0; i < valveList.size(); i++) {
    v = *valveList.get(i);
    Serial.print("Valve id : ");
    Serial.print(v.id);
    Serial.print(" | watering minutes : ");
    Serial.println(v.minutes_on);
  }
}

void loop() {


}
