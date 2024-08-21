SERVER_RUN_PARAMS = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True,
    "use_reloader": False,
    "log_output": True,
    # generate self-signed SSL certificate (so that JavaScript Web APIs that require HTTPS work)
    "ssl_context": "adhoc"
}

# address of the bluetooth device of this computer (the one you are using right now)
# JC's address: D8:12:65:88:74:74
# ZJ's address: 60:F2:62:A9:D8:CC
# YX's address: F8:89:D2:70:CA:BA
BLUETOOTH_ADDRESS = "60:F2:62:A9:D8:CC"
BLUETOOTH_CHANNEL = 5 # random number

do_bluetooth = False

VIDEO_CAPTURE_DEVICE_INDEX = 3

# socket.io event names
EVNAME_SEND_IMAGE = "data-url"
EVNAME_SEND_DEFAULT_HSV_COLOURS = "default-hsv-colours"
EVNAME_RECEIVE_HSV_COLOURS_UPDATE = "hsv-colours-update"
EVNAME_RECEIVE_CURRENT_ORIENTATION = "orientation"

SEND_TO_EV3_INTERVAL = 250 * pow(10, 6) # nanoseconds (milliseconds * 10^6)

import numpy as np
# lower and upper bounds for the colours in HSV
# HSV range in cv2: H [0, 179], S [0, 255], [0, 255]
# in HSV, there are two sections of red (start & end) and one section of blue
RED1_LOWER = np.array([0, 150, 150])
RED1_UPPER = np.array([10, 255, 255])

RED2_LOWER = np.array([170, 150, 150])
RED2_UPPER = np.array([180, 255, 255])

BLUE_LOWER = np.array([90, 150, 150])
BLUE_UPPER = np.array([120, 255, 255])

col_dict = {
    "red1lower": RED1_LOWER,
    "red1upper": RED1_UPPER,
    "red2lower": RED2_LOWER,
    "red2upper": RED2_UPPER,
    "bluelower": BLUE_LOWER,
    "blueupper": BLUE_UPPER,
}

RED_REAL_OBJECT_WIDTH = 1.5
BLUE_REAL_OBJECT_WIDTH = 8.5

# focal length of the camera
FOCAL_LENGTH = 500

MIN_CONTOUR_AREA = 500
# maximum number of pixels from midpoint (on the x-axis) that will be considered centre 
CENTRE_RANGE = 25

import logging
SOCKETIO_LOGGER_LEVEL = logging.DEBUG
BLUETOOTH_LOGGER_LEVEL = logging.DEBUG