
# For the other watering puck node, i insisted the code get a time info
# packet.  Why do I need this? The Rasp Pi software will let the watering
# puck know when to start watering and for how long. I originally had the
# time info for putting the chip to sleep.  However, for now, always on.
import board
from watering_puck_lib import WateringPuck
NODE_ID = 5
pin = board.D11

if __name__ == "__main__":
    watering_puck = WateringPuck(NODE_ID, pin)
    while True:
        watering_puck.packet_check()
