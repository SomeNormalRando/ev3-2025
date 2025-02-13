#!/usr/bin/env python3
import logging
logging.basicConfig(
    format="\x1b[30m[%(asctime)s \x1b[33m%(name)s\x1b[30m %(levelname)s] \x1b[97m%(message)s\x1b[0m", 
    datefmt="%H:%M:%S",
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)
logger.info("main.py executing")

from threading import Thread
from ev3dev2.led import Leds

LEDs = Leds()

LEDs.set_color("LEFT", "RED")
LEDs.set_color("RIGHT", "RED")


logger.info("initialising CleanSweep...")

from CleanSweep import CleanSweep

LEDs.set_color("LEFT", "AMBER")
LEDs.set_color("RIGHT", "AMBER")

robot = CleanSweep()

# controller_read_loop_thread = Thread(target = robot.controller_read_loop)
# controller_read_loop_thread.start()

# motors_loop_thread = Thread(target = robot.activekeys_loop)
# motors_loop_thread.start()


from bluetooth import bluetooth_loop

bluetooth_loop_thread = Thread(target = bluetooth_loop, args = [robot])
bluetooth_loop_thread.start()


LEDs.set_color("LEFT", "GREEN")
LEDs.set_color("RIGHT", "GREEN")