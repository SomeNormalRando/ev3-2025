#!/usr/bin/env python3
import logging
logging.basicConfig(
    format="\x1b[30m[%(asctime)s \x1b[33m%(name)s\x1b[30m %(levelname)s] \x1b[97m%(message)s\x1b[0m", 
    datefmt="%H:%M:%S",
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

logger.info("main.py executing")
bl_logger = logging.getLogger("bluetooth")

from json import loads
from json.decoder import JSONDecodeError
import socket
import logging
from threading import Thread
from ev3dev2.led import Leds

CODE_FG_BRIGHT_BLUE = "\x1b[94m"

LEDs = Leds()

LEDs.set_color("LEFT", "RED")
LEDs.set_color("RIGHT", "RED")

logger.info("initialising CleanSweep...")

from CleanSweep import CleanSweep


LEDs.set_color("LEFT", "AMBER")
LEDs.set_color("RIGHT", "AMBER")

robot = CleanSweep()

controller_read_loop_thread = Thread(target = robot.controller_read_loop)
controller_read_loop_thread.start()


motors_loop_thread = Thread(target = robot.activekeys_loop)
motors_loop_thread.start()

def start_receive_loop():
    BLUETOOTH_ADDRESS = "60:F2:62:A9:D8:CC"
    CHANNEL = 5

    # create a socket object with Bluetooth, TCP & RFCOMM
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
        try:
            s.connect((BLUETOOTH_ADDRESS, CHANNEL))
        except ConnectionError as err:
            bl_logger.error("Failed to connect:")
            bl_logger.error(err)
            return

        bl_logger.info("{}successfully connected to server (address {}, channel {})".format(CODE_FG_BRIGHT_BLUE, BLUETOOTH_ADDRESS, CHANNEL))
        # robot.connected_to_server = True

        try:
            bl_logger.info("{}started Bluetooth socket receive loop".format(CODE_FG_BRIGHT_BLUE))
            while True:
                if (robot.auto_mode == False):
                    continue

                raw_data = s.recv(1024)

                if not raw_data:
                    bl_logger.info("{}{{Bluetooth socket}} disconnected from {}".format(BLUETOOTH_ADDRESS).format(CODE_FG_BRIGHT_BLUE))
                    break

                data_str = raw_data.decode()
                bl_logger.debug("\x1b[30mdata received: {}".format(data_str))
                data_json = []
                try:
                    data_json = loads(data_str)
                except JSONDecodeError as err:
                    bl_logger.info("JSONDecodeError (this is normal, happens because `s.recv()` builds up unreceived data)")
                    continue

                if len(data_json) == 0:
                    robot.closest_detected_obj = None
                    continue

                # data format: [ [[centre_x, centre_y], distance, location], [[centre_x, centre_y], distance, location] ]

                # find value of min distance
                min_val = min(obj[1] for obj in data_json)
                # get the object that has the min distance
                for obj in data_json:
                    if obj[1] == min_val:
                        robot.closest_detected_obj = obj
                        break

        except ConnectionError as err:
            bl_logger.error("{}connection error (robot most likely disconnected from server):".format(CODE_FG_BRIGHT_BLUE), err)
            robot.connected_to_server = False

receive_loop_thread = Thread(target = start_receive_loop)
receive_loop_thread.start()


LEDs.set_color("LEFT", "GREEN")
LEDs.set_color("RIGHT", "GREEN")