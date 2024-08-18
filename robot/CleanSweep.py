from config import RECEIVE_FROM_SERVER_INTERVAL, COL_CODE_DEBUG, COL_CODE_FG_GREEN

import logging
logger = logging.getLogger("CleanSweep")

logger.info("loading modules...")

import evdev # type: ignore
from PS4Keymap import PS4Keymap
# from datetime import datetime
from time import sleep, time

from ev3dev2.motor import MoveJoystick, LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C
from ev3dev2 import DeviceNotFound

from enum import Enum
from typing import Tuple, Union

logger.info("modules loaded")

class ForwardOrLeftOrRight(Enum):
    left = -1
    forward = 0
    right = 1

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
        self.closest_detected_obj = None # type: Union[None, Tuple[list[int], int, ForwardOrLeftOrRight]]

        # counts how many times robot has moved forward / turned since auto mode started
        # self.forward_count = 0 # positive only
        # self.turn_count = 0 # sum of all lefts (-1) and rights (1), can be negative

        # list of every forward (0) / left (-1) / right (1) movement the robot has taken since the start of auto mode
        self.movements = [] # type: list[ForwardOrLeftOrRight]

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

        last = 0
        now = 0

        while True:
            self.active_keys = self.controller.active_keys()

            if self.auto_mode is True:
                now = time() * 1000.0
                while (now - last) < RECEIVE_FROM_SERVER_INTERVAL:
                    sleep(0.01)
                    now = time() * 1000.0
                last = now

                self.run_auto_mode()
            else:
                if PS4Keymap.BTN_R1.value in self.active_keys:
                    self.auto_mode = True
                    logger.info("{}[R1] automatic mode ACTIVATED - controller disabled".format(COL_CODE_FG_GREEN))
                    continue

                self.run_motors()

    def run_auto_mode(self):
        if PS4Keymap.BTN_R2.value in self.active_keys:
            logger.info("{}[R2] robot retracing steps...".format(COL_CODE_FG_GREEN))

            self.retrace_steps()

            logger.info("{}robot finished retracing steps".format(COL_CODE_FG_GREEN))

            logger.info("{}automatic mode STOPPED - controller enabled".format(COL_CODE_FG_GREEN))
            self.auto_mode = False
            return

        # if no detected objects, go straight
        detected_obj_location_id = ForwardOrLeftOrRight.forward

        if self.closest_detected_obj is None:
            logger.debug("{}self.closest_detected_obj is None".format(COL_CODE_DEBUG))
        else:
            # data format: [[centre_x, centre_y], distance, location]
            detected_obj_location_id = self.closest_detected_obj[2]
            logger.debug("{}detected_obj_location_id: {}".format(COL_CODE_DEBUG, detected_obj_location_id))


        self.move_forward_or_turn(detected_obj_location_id)


        self.movements.append(detected_obj_location_id)

    def run_motors(self):
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
                logger.info("{}[X] MoveJoystick speed - REDUCED".format(COL_CODE_FG_GREEN))
                self.reduce_movejoystick_speed = True
            else:
                logger.info("{}[X] MoveJoystick speed - NORMAL".format(COL_CODE_FG_GREEN))
                self.reduce_movejoystick_speed = False

    def retrace_steps(self):
        last = 0
        now = 0

        logger.debug("{}`retrace_steps` - `self.movements` = {}".format(COL_CODE_DEBUG, self.movements))

        reversed_movements = reversed(self.movements)
        for (index, movement_id) in enumerate(reversed_movements):
            logger.debug("{}`retrace_steps` - movement {}".format(COL_CODE_DEBUG, index))

            # time_ns() was added in 3.7, ev3dev runs 3.5.3
            now = time() * 1000.0
            while (now - last) < RECEIVE_FROM_SERVER_INTERVAL:
                sleep(0.01)
                now = time() * 1000.0
            last = now

            if movement_id == ForwardOrLeftOrRight.forward:
                self.move_joystick.on(
                    0, # go backwards
                    -CleanSweep._AUTO_FORWARD_SPEED,
                    CleanSweep.JOYSTICK_SCALE_RADIUS
                )
            elif movement_id == ForwardOrLeftOrRight.left:
                self.move_forward_or_turn(ForwardOrLeftOrRight.right)
            elif movement_id == ForwardOrLeftOrRight.right:
                self.move_forward_or_turn(ForwardOrLeftOrRight.left)

        self.movements = []

    def move_forward_or_turn(self, movement_type: ForwardOrLeftOrRight):
        if movement_type == ForwardOrLeftOrRight.forward:
            self.move_joystick.on(
                0, # go straight
                CleanSweep._AUTO_FORWARD_SPEED,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif movement_type == ForwardOrLeftOrRight.left:
            self.move_joystick.on(
                -CleanSweep._AUTO_FORWARD_SPEED, # turn left (in place)
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif movement_type == ForwardOrLeftOrRight.right:
            self.move_joystick.on(
                CleanSweep._AUTO_FORWARD_SPEED, # turn right (in place)
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
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