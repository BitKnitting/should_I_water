/*
   The Valve class simplifies turning on and off valves hooked up to
   the water used for irrigation.
*/



/*
   These are the gpio pins on the Feather used by the three valves in our backyard.
*/
const uint8_t yellow_gpio = 12;
const uint8_t blue_gpio = 11;
const uint8_t green_gpio = 6;
/*
   A timer is used to go off after the number of minutes the caller told us to keep
   the valve on.  When the timer goes off, the user's callback is run.
*/
#include "Timer.h"
Timer t;


// The Valve class helps us control one of the valves to turn on/off for watering plants.
class Valve
{
  public:
    uint8_t           id;  // The GPIO pin on the Feather assigned to this valve.
    uint8_t           minutes_on;  // The number of minutes to water.
    int               timer; // the id assigned to the timer.  This is used to turn the timer
                            // off in the case a request comes in to start watering before it's done.
    void              (*callback)(void); // The function to call in the caller's code when
                                         // the "watering complete" timer goes off.

    Valve(uint8_t gpio_pin)
    {
      timer = 0;
      id = gpio_pin;
      pinMode(id, OUTPUT);
    }
    /*
       Start watering turns the valve on and sets a timer.  Before we do this,
       let's make sure to clean up if the valve is in the process of watering.
       To clean up, we stop the timer and turn off the valve.
    */
    void start_watering(void (*callback)(), uint8_t watering_minutes) {
      
      stop_watering();
      // Turn on the valve and start the timer.
      digitalWrite(id, HIGH);
      minutes_on = watering_minutes;

      long ms_on = minutes_on * 60 * 1000;
      // After ms_on ms, the timer goes off and the caller's function runs.
      timer = t.after(ms_on, (*callback));

    }
    // To clean up, we stop the timer and turn off the valve.
    void stop_watering() {
      digitalWrite(id, LOW);
      if (timer) {
        t.stop(timer);
        timer = 0;
      }
    }

};

