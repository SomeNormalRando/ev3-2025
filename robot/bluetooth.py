from config import BLUETOOTH_ADDRESS, CHANNEL, COL_CODE_BL_LOGGER, COL_CODE_DEBUG

import logging
bl_logger = logging.getLogger("bluetooth")
bl_logger.setLevel(logging.DEBUG)

from json import loads
from json.decoder import JSONDecodeError

import socket
from CleanSweep import CleanSweep

def recv_loop(sock: socket.socket, robot: CleanSweep):
    while True:
        if (robot.auto_mode == False):
            continue

        raw_data = sock.recv(1024)

        if not raw_data:
            bl_logger.info("{}no `raw_data`, (likely disconnected)".format(BLUETOOTH_ADDRESS).format(COL_CODE_BL_LOGGER))
            break

        data_str = raw_data.decode()
        bl_logger.debug("{}data received: {}".format(COL_CODE_DEBUG, data_str))

        data_json = []
        try:
            data_json = loads(data_str)
        except JSONDecodeError:
            bl_logger.info("{}JSONDecodeError (this is normal, happens because `s.recv()` builds up unreceived data)".format(COL_CODE_DEBUG))
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