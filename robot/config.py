import logging
bl_logger = logging.getLogger("bluetooth")
bl_logger.setLevel(logging.INFO)

cs_logger = logging.getLogger("CleanSweep")
cs_logger.setLevel(logging.DEBUG)

BLUETOOTH_ADDRESS = "E4:B3:18:64:F3:DD"
CHANNEL = 5

RECEIVE_FROM_SERVER_INTERVAL = 250 # same as SEND_TO_EV3_INTERVAL in ../server/config.py except in ms instead of ns

# foreground grey
COL_CODE_DEBUG = "\x1b[30m"
COL_CODE_FG_GREEN = "\x1b[32m"
# foreground bright blue
COL_CODE_BL_LOGGER = "\x1b[94m"