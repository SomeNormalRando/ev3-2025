CODE_FG_GREEN = "\x1b[32m"

import logging
logger = logging.getLogger(__name__)

logger.info("loading modules...")

import evdev # type: ignore
from PS4Keymap import PS4Keymap
# from datetime import datetime
from time import sleep

from ev3dev2.motor import MoveJoystick, LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C
from ev3dev2 import DeviceNotFound

from typing import Tuple

logger.info("modules loaded")

class CleanSweep:
    '''
    Receives input from a connected PS4 controller and runs the robot. 
    '''
    JOYSTICK_SCALE_RADIUS = 100
    JOYSTICK_THRESHOLD = 10
    OPENING_MOTOR_SPEED = 10

    MOVEMENT_SPEED_REDUCTION = 3

    # automatic mode
    _AUTO_FORWARD_SPEED = 12
    _AUTO_TURNING_SPEED = 2

    def __init__(self):
        self.controller = CleanSweep.find_ps4_controller()

        self.connect_inputs_and_outputs()

        self.active_keys = []

        self.joystick_x = 0.0
        self.joystick_y = 0.0

        self.auto_mode = False

        self.connected_to_server = False
        self.closest_detected_obj = None

        self.reduce_movejoystick_speed = False

    def connect_inputs_and_outputs(self):
        t = 5
        while True:
            try:
                self.move_joystick = MoveJoystick(OUTPUT_B, OUTPUT_C)

                self.opening_motor = MediumMotor(OUTPUT_A)
                self.left_motor = LargeMotor(OUTPUT_B)
                self.right_motor = LargeMotor(OUTPUT_C)

                # this break statement will only be reached if the above code executes without error
                break

            except DeviceNotFound as error:
                print()
                logger.error(error)
                logger.info("initialising again in {} seconds".format(t))
                sleep(t)

    def controller_read_loop(self):
        logger.info("started PS4 controller read loop")
        for event in self.controller.read_loop():
            # joystick [do not remove this condition]
            if event.type == 3 and self.auto_mode is False:
                raw_val = event.value
                if event.code == PS4Keymap.AXE_LX.value: # left joystick, X axis
                    self.joystick_x = CleanSweep.scale_joystick(raw_val)
                elif event.code == PS4Keymap.AXE_LY.value: # left joystick, Y axis
                    # "-" in front is to reverse the sign (+/-) of y (the y-axis of the PS4 joystick is reversed - see notes.md)
                    self.joystick_y = -(CleanSweep.scale_joystick(raw_val))

    def activekeys_loop(self):
        logger.info("started active_keys loop")
        while True:
            self.active_keys = self.controller.active_keys()
            if self.auto_mode is True:
                self.run_auto_mode()
            else:
                self.run_motors()

    def run_auto_mode(self):
        if PS4Keymap.BTN_R2.value in self.active_keys:
            self.auto_mode = False
            logger.info("{}automatic mode STOPPED - controller enabled".format(CODE_FG_GREEN))
            return

        # if no detected objects, go straight
        detected_obj_location_id = 0

        if self.closest_detected_obj is not None:
            # data format: [[centre_x, centre_y], distance, location]
            detected_obj_location_id = self.closest_detected_obj[2]

        if detected_obj_location_id == 0:
            self.move_joystick.on(
                0, # go straight
                CleanSweep._AUTO_FORWARD_SPEED,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif detected_obj_location_id == -1:
            self.move_joystick.on(
                -CleanSweep._AUTO_FORWARD_SPEED, # turn left
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif detected_obj_location_id == 1:
            self.move_joystick.on(
                CleanSweep._AUTO_FORWARD_SPEED, # turn right
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        else:
            logger.warning("run_auto_mode(): `detected_obj_location_id` is not -1, 0, or 1")

    def run_motors(self):
        if PS4Keymap.BTN_R1.value in self.active_keys:
            self.auto_mode = True
            logger.info("{}automatic mode ACTIVATED - controller disabled".format(CODE_FG_GREEN))
            return

        # MOTORS
        if self.reduce_movejoystick_speed == True:
            self.move_joystick.on(
                self.joystick_x / CleanSweep.MOVEMENT_SPEED_REDUCTION if abs(self.joystick_x) > CleanSweep.JOYSTICK_THRESHOLD else 0,
                self.joystick_y / CleanSweep.MOVEMENT_SPEED_REDUCTION if abs(self.joystick_y) > CleanSweep.JOYSTICK_THRESHOLD else 0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        else:
            self.move_joystick.on(
                self.joystick_x if abs(self.joystick_x) > CleanSweep.JOYSTICK_THRESHOLD else 0,
                self.joystick_y if abs(self.joystick_y) > CleanSweep.JOYSTICK_THRESHOLD else 0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )

        if PS4Keymap.BTN_L1.value in self.active_keys:
            self.opening_motor.on(CleanSweep.OPENING_MOTOR_SPEED)
        elif PS4Keymap.BTN_L2.value in self.active_keys:
            self.opening_motor.on(-CleanSweep.OPENING_MOTOR_SPEED)
        else:
            self.opening_motor.stop()

        if PS4Keymap.BTN_CROSS.value in self.active_keys:
            if self.reduce_movejoystick_speed == False:
                logger.info("{}MoveJoystick speed - REDUCED".format(CODE_FG_GREEN))
                self.reduce_movejoystick_speed = True
            else:
                logger.info("{}MoveJoystick speed - NORMAL".format(CODE_FG_GREEN))
                self.reduce_movejoystick_speed = False

    #region static methods
    @staticmethod
    def scale_range(val: float, src: Tuple[float, float], dst: Tuple[float, float]):
        MIN = src[0]
        MAX = src[1]
        NEW_MIN = dst[0]
        NEW_MAX = dst[1]
        a = (NEW_MAX - NEW_MIN) / (MAX - MIN)
        b = NEW_MAX - (a * MAX)
        return (a * val) + b

    @staticmethod
    def scale_joystick(val: float):
        return CleanSweep.scale_range(
            val,
            (0, 255),
            (-CleanSweep.JOYSTICK_SCALE_RADIUS, CleanSweep.JOYSTICK_SCALE_RADIUS)
        )

    @staticmethod
    def find_ps4_controller():
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        controller = None
        for device in devices:
            if device.name == "Wireless Controller":
                controller = device
                logger.info("found PS4 controller")
                return controller

        raise ConnectionError(str.format("PS4 controller not found (found devices: `{}`)", devices))
    #endregion