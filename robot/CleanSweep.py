from config import RECEIVE_FROM_SERVER_INTERVAL, COL_CODE_DEBUG, COL_CODE_FG_GREEN

import logging
cs_logger = logging.getLogger("CleanSweep")
cs_logger.setLevel(logging.DEBUG)

cs_logger.info("loading modules...")

import evdev # type: ignore
from PS4Keymap import PS4Keymap
# from datetime import datetime
from time import sleep, time

from ev3dev2.motor import MoveJoystick, LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C
from ev3dev2 import DeviceNotFound
from ev3dev2.led import Leds

LEDs = Leds()

from enum import Enum
from typing import Tuple, Union

cs_logger.info("modules loaded")

class ForwardOrLeftOrRight(Enum):
    left = -1
    forward = 0
    right = 1

class CleanSweep:
    '''Receives input from a connected PS4 controller and runs the robot. '''

    JOYSTICK_SCALE_RADIUS = 100
    '''joystick radius provided to MoveJoystick.on()'''

    MIN_JOYSTICK_THRESHOLD = 10
    '''minimum value of PS4 joystick values to move motors'''

    OPENING_MOTOR_SPEED = 25
    OPENING_MOTOR_DEGREES = 180

    MOVEMENT_SPEED_REDUCTION = 3

    # automatic mode
    _AUTO_FORWARD_SPEED = 12
    _AUTO_TURNING_SPEED = 2

    _AUTO_TURN_DURATION = 0.2
    '''[auto mode] duration to sleep while turning'''
    _AUTO_TURN_DELAY = 0.5
    '''[auto mode] duration to sleep after turning is finished'''

    def __init__(self):
        self.controller = CleanSweep.find_ps4_controller()

        self.connect_inputs_and_outputs()

        self.active_keys = []

        self.joystick_x = 0.0
        self.joystick_y = 0.0

        self.auto_mode = False
        self.closest_detected_obj = None # type: Union[None, Tuple[list[int], int, int]]

        # list of every forward (0) / left (-1) / right (1) movement the robot has taken since the start of auto mode
        # self.movements = [] # type: list[ForwardOrLeftOrRight]

        self.opener_open = False

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
                cs_logger.error(error)
                cs_logger.info("initialising again in {} seconds".format(t))
                sleep(t)

    def controller_read_loop(self):
        '''repeatedly reads left joystick input values from the PS4 controller'''
        cs_logger.info("started PS4 controller read loop")
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
        cs_logger.info("started active_keys loop")

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
                    cs_logger.info("{}[R1] automatic mode ACTIVATED - controller disabled".format(COL_CODE_FG_GREEN))

                    LEDs.set_color("LEFT", "YELLOW")
                    LEDs.set_color("RIGHT", "YELLOW")
                    continue

                self.run_motors()

    def run_auto_mode(self):
        '''runs repeatedly when `self.auto_mode` is `True`'''
        # if R2 button is pressed, stop automatic mode
        if PS4Keymap.BTN_R2.value in self.active_keys:
            cs_logger.info("{}automatic mode STOPPED - controller enabled".format(COL_CODE_FG_GREEN))
            self.auto_mode = False

            LEDs.set_color("LEFT", "GREEN")
            LEDs.set_color("RIGHT", "GREEN")
            return

        # move forward if no detected objects
        detected_obj_direction = ForwardOrLeftOrRight.forward

        if self.closest_detected_obj is not None:
            detected_obj_direction = ForwardOrLeftOrRight(self.closest_detected_obj[2])

        self.move_forward_or_turn(detected_obj_direction)

        # Small sleep to avoid CPU overuse
        sleep(0.01)

    # these two functions are run from bluetooth.py when obstacles_detected is True (open) or False (close)
    def open_opener(self):
        cs_logger.info("opening opener")
        self.opener_open = True
        self.opening_motor.on_for_degrees(CleanSweep.OPENING_MOTOR_SPEED, -CleanSweep.OPENING_MOTOR_DEGREES)
    def close_opener(self):
        cs_logger.info("closing opener")
        self.opener_open = False
        self.opening_motor.on_for_degrees(CleanSweep.OPENING_MOTOR_SPEED, CleanSweep.OPENING_MOTOR_DEGREES)

    def run_motors(self):
        '''runs repeatedly when `self.auto_mode` is `False`'''
        speed_x = self.joystick_x if abs(self.joystick_x) > CleanSweep.MIN_JOYSTICK_THRESHOLD else 0
        speed_y = self.joystick_y if abs(self.joystick_y) > CleanSweep.MIN_JOYSTICK_THRESHOLD else 0

        if self.reduce_movejoystick_speed is True:
            speed_x /= CleanSweep.MOVEMENT_SPEED_REDUCTION
            speed_y /= CleanSweep.MOVEMENT_SPEED_REDUCTION

        self.move_joystick.on(
            speed_x,
            speed_y,
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
                self.reduce_movejoystick_speed = True
                cs_logger.info("{}[X] MoveJoystick speed - REDUCED".format(COL_CODE_FG_GREEN))
                sleep(0.01)
            else:
                self.reduce_movejoystick_speed = False
                cs_logger.info("{}[X] MoveJoystick speed - NORMAL".format(COL_CODE_FG_GREEN))
                sleep(0.01)

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
            sleep(CleanSweep._AUTO_TURN_DURATION)

            self.move_joystick.off()
            sleep(CleanSweep._AUTO_TURN_DELAY)
        elif movement_type == ForwardOrLeftOrRight.right:
            self.move_joystick.on(
                CleanSweep._AUTO_FORWARD_SPEED, # turn right (in place)
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
            sleep(CleanSweep._AUTO_TURN_DURATION)

            self.move_joystick.off()
            sleep(CleanSweep._AUTO_TURN_DELAY)

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
                cs_logger.info("found PS4 controller")
                return controller

        raise ConnectionError(str.format("PS4 controller not found (found devices: `{}`)", devices))
    #endregion