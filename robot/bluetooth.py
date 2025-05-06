from config import BLUETOOTH_ADDRESS, CHANNEL, COL_CODE_BL_LOGGER, COL_CODE_DEBUG, COL_CODE_FG_GREEN, MovementCommand

import logging
bl_logger = logging.getLogger("bluetooth")
bl_logger.setLevel(logging.INFO)

from json import loads
from json.decoder import JSONDecodeError

from threading import Thread

import socket
from CleanSweep import CleanSweep

from ev3dev2.led import Leds

LEDs = Leds()

def recv_loop(sock: socket.socket, robot: CleanSweep):
    while True:
        # if (robot.auto_mode == False):
        #     continue

        raw_data = sock.recv(1024)

        data_str = raw_data.decode()
        bl_logger.debug("{}data received: {}".format(COL_CODE_DEBUG, data_str))

        data_json = None
        try:
            data_json = loads(data_str)
        except JSONDecodeError:
            # this is normal because `s.recv()` builds up previous sent data that was not `recv`ed
            bl_logger.debug("{}JSONDecodeError (started receiving data)".format(COL_CODE_DEBUG))
            continue

        # if data_json is a dict then it is a command
        if isinstance(data_json, dict):
            type = data_json.get("type")
            if type == "MOVEMENT":
                robot.move_by_command(MovementCommand(data_json.get("direction")), data_json.get("speed"))
            elif type == "FUNNEL":
                robot.rotate_funnel(data_json.get("command"))
            elif type == "AUTO_MODE":
                command = data_json.get("command")
                if command == 0:
                    robot.auto_mode = False
                    bl_logger.info("{}automatic mode STOPPED".format(COL_CODE_FG_GREEN))

                    LEDs.set_color("LEFT", "GREEN")
                    LEDs.set_color("RIGHT", "GREEN")
                elif command == 1:
                    robot.auto_mode = True

                    bl_logger.info("{}automatic mode STARTED".format(COL_CODE_FG_GREEN))
                    LEDs.set_color("LEFT", "YELLOW")
                    LEDs.set_color("RIGHT", "YELLOW")

                    auto_mode_thread = Thread(target = robot.start_auto_mode_loop)
                    auto_mode_thread.start()
            continue

        # if data_json is a list then it is the detected objects from colour_detection_loop
        red_detected_objects = data_json[0]

        if red_detected_objects is not None:
            if len(red_detected_objects) == 0:
                robot.closest_detected_obj = None
                continue

            # ? data format: [ [[centre_x, centre_y], distance, location], [[centre_x, centre_y], distance, location] ]

            # find value of min distance
            min_val = min(obj[1] for obj in red_detected_objects)
            # get the object that has the min distance
            for obj in red_detected_objects:
                if obj[1] == min_val:
                    robot.closest_detected_obj = obj
                    break


def bluetooth_loop(robot: CleanSweep):
    bl_logger.info("{}attempting to connect to server...".format(COL_CODE_BL_LOGGER))

    # create a socket object with Bluetooth, TCP & RFCOMM
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
        try:
            sock.connect((BLUETOOTH_ADDRESS, CHANNEL))
        except ConnectionError as err:
            bl_logger.error("{}Failed to connect:".format(COL_CODE_BL_LOGGER))
            bl_logger.error(err)
            exit()

        bl_logger.info("{}successfully connected to server (address {}, channel {})".format(COL_CODE_BL_LOGGER, BLUETOOTH_ADDRESS, CHANNEL))

        bl_logger.info("{}started Bluetooth socket recv loop".format(COL_CODE_BL_LOGGER))

        try:
            recv_loop(sock, robot)
        except ConnectionError as err:
            bl_logger.error("{}connection error in `recv_loop()` (likely disconnected):".format(COL_CODE_BL_LOGGER), err)