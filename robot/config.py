from enum import Enum

BLUETOOTH_ADDRESS = "60:F2:62:A9:D8:CC"
CHANNEL = 5

RECEIVE_FROM_SERVER_INTERVAL = 250 # same as SEND_TO_EV3_INTERVAL in ../server/config.py except in ms instead of ns

# foreground grey
COL_CODE_DEBUG = "\x1b[30m"
# foreground bright blue
COL_CODE_BL_LOGGER = "\x1b[94m"

COL_CODE_FG_GREEN = "\x1b[32m"

class MovementCommand(Enum):
    STOP = -2
    FORWARD_CONTINUOUSLY = 0
    BACKWARD_CONTINUOUSLY = 2
    TURN_LEFT_CONTINUOUSLY = 3
    TURN_RIGHT_CONTINUOUSLY = 4
    TURN_A_LITTLE_LEFT = -1
    TURN_A_LITTLE_RIGHT = 1