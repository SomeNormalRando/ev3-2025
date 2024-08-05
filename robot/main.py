#!/usr/bin/env python3
from json import loads
from json.decoder import JSONDecodeError
import socket
import logging
from threading import Thread
from ev3dev2.led import Leds

logging.basicConfig(
    format="\x1b[30m[%(asctime)s \x1b[33m%(levelname)s\x1b[30m] \x1b[34m%(message)s\x1b[0m", 
    datefmt="%H:%M:%S",
    level=logging.DEBUG
)

CODE_FG_BRIGHT_BLUE = "\x1b[94m"

logging.info("main.py running.")

LEDs = Leds()

LEDs.set_color("LEFT", "RED")
LEDs.set_color("RIGHT", "RED")

logging.info("Initialising CleanSweep...")

from CleanSweep import CleanSweep


LEDs.set_color("LEFT", "AMBER")
LEDs.set_color("RIGHT", "AMBER")

robot = CleanSweep()

controller_read_loop_thread = Thread(target = robot.start_controller_read_loop)
controller_read_loop_thread.start()


motors_loop_thread = Thread(target = robot.start_motors_and_activekeys_loop)
motors_loop_thread.start()

def start_receive_loop():
    # JC's laptop address: D8:12:65:88:74:74
    BLUETOOTH_ADDRESS = "60:f2:62:a9:d8:cc"
    CHANNEL = 5

    # create a socket object with Bluetooth, TCP & RFCOMM
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
        try:
            s.connect((BLUETOOTH_ADDRESS, CHANNEL))
        except ConnectionError as err:
            logging.error("Failed to connect:", err)
            return

        logging.info("{}Successfully connected to server (bluetooth device {}, channel {}).".format(CODE_FG_BRIGHT_BLUE, BLUETOOTH_ADDRESS, CHANNEL))
        # robot.connected_to_server = True

        try:
            logging.info("{}Started Bluetooth socket receive loop.".format(CODE_FG_BRIGHT_BLUE))
            while True:
                # recv even if auto mode is not True so that raw_data doesn't build up into [][][][]
                if (robot.auto_mode != True):
                    continue

                raw_data = s.recv(1024)

                if not raw_data:
                    logging.info("{}{{Bluetooth socket}} Disconnected from {}.".format(BLUETOOTH_ADDRESS).format(CODE_FG_BRIGHT_BLUE))
                    break

                data_str = raw_data.decode()
                logging.debug("\x1b[30mData received: {}".format(data_str))

                data_json = loads(data_str)
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

        except JSONDecodeError as err:
            logging.error("JSONDecodeError (this is normal, happens because `s.recv()` builds up unreceived data)")

        except ConnectionError as err:
            logging.error("{}Connection error (robot most likely disconnected from server):".format(CODE_FG_BRIGHT_BLUE), err)
            robot.connected_to_server = False

# COMMENT THESE TWO LINES TO STOP PUBLISHING MESSAGES THROUGH BLUETOOTH SOCKET
# send_loop_thread = Thread(target = start_send_loop, args=[robot])
receive_loop_thread = Thread(target = start_receive_loop)
receive_loop_thread.start()


LEDs.set_color("LEFT", "GREEN")
LEDs.set_color("RIGHT", "GREEN")