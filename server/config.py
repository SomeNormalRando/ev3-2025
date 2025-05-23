SERVER_RUN_PARAMS = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True,
    "use_reloader": False,
    "log_output": True,
}

# address of the bluetooth device of this computer (the one you are using right now)
# JC's address: D8:12:65:88:74:74
# ZJ's address: 60:F2:62:A9:D8:CC
# YX's address: F8:89:D2:70:CA:BA
BLUETOOTH_ADDRESS = "60:F2:62:A9:D8:CC"
BLUETOOTH_CHANNEL = 5 # random number

CONNECT_TO_EV3 = False

VIDEO_CAPTURE_DEVICE_INDEX = 3

# socket.io event names
EVNAME_SEND_IMAGE = "data-url"
EVNAME_SEND_DEFAULT_HSV_COLOURS = "default-hsv-colours"
EVNAME_RECEIVE_HSV_COLOURS_UPDATE = "hsv-colours-update"
EVNAME_RECEIVE_MOVEMENT_COMMAND = "movement-command"
EVNAME_RECEIVE_FUNNEL_COMMAND = "funnel-command"
EVNAME_RECEIVE_AUTO_MODE_COMMAND = "auto-mode-command"

SEND_TO_EV3_INTERVAL = 250 * pow(10, 6) # nanoseconds (milliseconds * 10^6)

import numpy as np
# lower and upper bounds for the colours in HSV
# HSV range in cv2: H [0, 179], S [0, 255], [0, 255]
# in HSV, there are two sections of red (start & end) and one section of blue
RED1_LOWER = np.array([0, 150, 200])
RED1_UPPER = np.array([10, 255, 255])

RED2_LOWER = np.array([170, 150, 150])
RED2_UPPER = np.array([180, 255, 255])

BLUE_LOWER = np.array([80, 0, 200])
BLUE_UPPER = np.array([120, 255, 255])

YELLOW_LOWER = np.array([15, 150, 150])
YELLOW_UPPER = np.array([30, 255, 255])

col_dict = {
    "red1lower": RED1_LOWER,
    "red1upper": RED1_UPPER,
    "red2lower": RED2_LOWER,
    "red2upper": RED2_UPPER,
    "bluelower": BLUE_LOWER,
    "blueupper": BLUE_UPPER,
    "yellowlower": YELLOW_LOWER,
    "yellowupper": YELLOW_UPPER,
}

RED_REAL_OBJECT_WIDTH = 1.5
BLUE_REAL_OBJECT_WIDTH = 8.5
YELLOW_REAL_OBJECT_WIDTH = 1

# focal length of the camera
FOCAL_LENGTH = 500

MIN_CONTOUR_AREA = 500

# maximum number of pixels from midpoint (on the x-axis) that will be considered centre 
CENTRE_RANGE = 35

import logging
SOCKETIO_LOGGER_LEVEL = logging.DEBUG
BLUETOOTH_LOGGER_LEVEL = logging.DEBUG