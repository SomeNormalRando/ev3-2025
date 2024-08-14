SERVER_PORT = 8000

# address of the bluetooth device of this computer (the one you are using right now)
# JC's address: D8:12:65:88:74:74
# ZJ's address: 60:F2:62:A9:D8:CC
# YX's address: F8:89:D2:70:CA:BA
BLUETOOTH_ADDRESS = "60:F2:62:A9:D8:CC"

BLUETOOTH_CHANNEL = 5 # random number

do_bluetooth = True

VIDEO_CAPTURE_DEVICE_INDEX = 1

SOCKETIO_EVENT_NAME = "data-url"

SEND_TO_EV3_EVERY = 250 * pow(10, 6) # nanoseconds (milliseconds * 10^6)