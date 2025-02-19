from config import RECEIVE_FROM_SERVER_INTERVAL, COL_CODE_DEBUG, COL_CODE_FG_GREEN, MovementCommand

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

from typing import Tuple, Union

cs_logger.info("modules loaded")

class CleanSweep:
    '''Receives input from a connected PS4 controller and runs the robot. '''

    JOYSTICK_SCALE_RADIUS = 100
    '''joystick radius provided to `MoveJoystick.on()`'''

    MIN_JOYSTICK_THRESHOLD = 10
    '''minimum value of PS4 joystick values to move motors'''

    FUNNEL_MOTOR_SPEED = 40
    FUNNEL_MOTOR_DEGREES = 180

    MOVEMENT_SPEED_REDUCTION = 3

    INTERFACE_CONTROL_SPEED = 80

    # automatic mode
    AUTO_FORWARD_SPEED = 12
    AUTO_TURNING_SPEED = 2

    AUTO_TURN_DURATION = 0.2
    '''[command / auto mode] duration to sleep while turning'''
    AUTO_TURN_DELAY = 0.5
    '''[command / auto mode] duration to sleep after turning is finished'''

    INPUT_OUTPUT_NOT_CONNECTED_WAIT_DURATION = 5

    def __init__(self):
        # self.controller = CleanSweep.find_ps4_controller()

        self.connect_inputs_and_outputs()

        # self.active_keys = []

        # self.joystick_x = 0.0
        # self.joystick_y = 0.0

        self.auto_mode = False
        self.closest_detected_obj = None # type: Union[None, Tuple[list[int], int, int]]

        self.reduce_movejoystick_speed = False

    def connect_inputs_and_outputs(self):
        while True:
            try:
                self.move_joystick = MoveJoystick(OUTPUT_B, OUTPUT_C)

                self.funnel_motor = MediumMotor(OUTPUT_A)
                self.left_motor = LargeMotor(OUTPUT_B)
                self.right_motor = LargeMotor(OUTPUT_C)

                # this break statement will only be reached if the above code executes without error
                break

            except DeviceNotFound as error:
                print()
                cs_logger.error(error)
                cs_logger.info("initialising again in {} seconds".format(CleanSweep.INPUT_OUTPUT_NOT_CONNECTED_WAIT_DURATION))
                sleep(CleanSweep.INPUT_OUTPUT_NOT_CONNECTED_WAIT_DURATION)

    def start_auto_mode_loop(self):
        while True:
            if self.auto_mode is False:
                self.move_by_command(MovementCommand.STOP, 0)
                break

            # move forward if no detected objects
            detected_obj_direction = MovementCommand.FORWARD_CONTINUOUSLY

            if self.closest_detected_obj is not None:
                detected_obj_direction = MovementCommand(self.closest_detected_obj[2])

            self.move_by_command(detected_obj_direction, CleanSweep.AUTO_FORWARD_SPEED)

            # small sleep to avoid CPU overuse
            sleep(0.01)

    def move_by_command(self, movement_type: MovementCommand, speed):
        if movement_type == MovementCommand.STOP:
            self.move_joystick.off()

        # continuous commands
        elif movement_type == MovementCommand.FORWARD_CONTINUOUSLY:
            self.move_joystick.on(
                0, # go straight
                speed,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif movement_type == MovementCommand.BACKWARD_CONTINUOUSLY:
            self.move_joystick.on(
                0, # go straight backwards
                -speed,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif movement_type == MovementCommand.TURN_LEFT_CONTINUOUSLY:
            self.move_joystick.on(
                -speed, # turn left (in place)
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
        elif movement_type == MovementCommand.TURN_RIGHT_CONTINUOUSLY:
            self.move_joystick.on(
                speed, # turn right (in place)
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )

        # discrete commands
        elif movement_type == MovementCommand.TURN_A_LITTLE_LEFT:
            self.move_joystick.on(
                -speed, # turn left (in place)
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
            sleep(CleanSweep.AUTO_TURN_DURATION)

            self.move_joystick.off()
            sleep(CleanSweep.AUTO_TURN_DELAY)
        elif movement_type == MovementCommand.TURN_A_LITTLE_RIGHT:
            self.move_joystick.on(
                speed, # turn right (in place)
                0,
                CleanSweep.JOYSTICK_SCALE_RADIUS
            )
            sleep(CleanSweep.AUTO_TURN_DURATION)

            self.move_joystick.off()
            sleep(CleanSweep.AUTO_TURN_DELAY)

    def rotate_funnel(self, command):
        if command == 0:
            self.funnel_motor.off()
        elif command == -1:
            self.funnel_motor.on(
                CleanSweep.FUNNEL_MOTOR_SPEED,
            )
        elif command == 1:
            self.funnel_motor.on(
                -CleanSweep.FUNNEL_MOTOR_SPEED,
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
                cs_logger.info("found PS4 controller")
                return controller

        raise ConnectionError(str.format("PS4 controller not found (found devices: `{}`)", devices))
    #endregion