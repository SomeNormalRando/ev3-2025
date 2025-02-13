import numpy as np
import numpy.typing
import cv2
import base64

from detect_colour import detect_colour_and_draw

from json import dumps as stringify_json
from time import time_ns

import flask_socketio
import socket

import logging
logger = logging.getLogger(__name__)
socketio_logger = logging.getLogger("socket.io")

from config import col_dict, VIDEO_CAPTURE_DEVICE_INDEX, EVNAME_SEND_IMAGE, EVNAME_RECEIVE_HSV_COLOURS_UPDATE, SEND_TO_EV3_INTERVAL

def ndarray_to_b64(ndarray: numpy.typing.NDArray):
    return base64.b64encode(ndarray.tobytes()).decode()

def start_colour_detection_loop(socketio_app: flask_socketio.SocketIO, client_sock: socket.socket | None):
    '''
    provide `None` as `client_sock` to **not** send data to EV3
    '''
    logger.info("started colour_detection_loop")

    @socketio_app.on(EVNAME_RECEIVE_HSV_COLOURS_UPDATE)
    def receive_hsv_colours_update(colourName, new_colours):
        # if <input> is empty (e.g. user backspaces) the corresponding colour value will be None
        # None as a colour value will cause errors in cv2 functions, so skip if colours contain None
        has_non_int = not all(isinstance(x, int) for x in new_colours)
        if (has_non_int is True):
            socketio_logger.debug(f"HSV colours update: {colourName} {new_colours} contains non-integer, skipping `col_dict` update")
            return

        socketio_logger.debug(f"\x1b[30mHSV colours update: {colourName} {new_colours}")
        col_dict[colourName] = np.array(new_colours)

    capture = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE_INDEX, cv2.CAP_DSHOW) 

    if not capture.isOpened():
        logger.error("could not open video stream")
        return

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not capture.isOpened():
        logger.error("could not open video stream")
        return

    # Get the width of the video frame
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    midpoint_x = frame_width // 2 # double / is floor division

    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print()
    logger.info(f"opened video capture from device {VIDEO_CAPTURE_DEVICE_INDEX}")
    logger.info(f"video dimensions: {frame_width} × {frame_height}\n")

    last = 0
    now = 0
    while True:
        now = time_ns()

        retval, raw_frame = capture.read()
        if not retval:
            logger.error("could not read frame")
            return

        (processed_frame, red_detected_objects, blue_detected_objects) = detect_colour_and_draw(
            raw_frame, midpoint_x,
            col_dict["red1lower"], col_dict["red1upper"],
            col_dict["red2lower"], col_dict["red2upper"],
            col_dict["bluelower"], col_dict["blueupper"],
        )

        (retval, jpg_image) = cv2.imencode(".jpg", processed_frame)

        if retval is False:
            logger.warning("image encoding unsuccessful, skipping frame")
            continue

        # send to server
        socketio_app.emit(EVNAME_SEND_IMAGE, {
            "b64ImageData": ndarray_to_b64(jpg_image),
            "redDetectedObjects": red_detected_objects,
            "blueDetectedObjects": blue_detected_objects,
        })


        if client_sock is not None and (now - last) > SEND_TO_EV3_INTERVAL:
            last = now
            try:
                # send to EV3
                client_sock.sendall(stringify_json([red_detected_objects]).encode())
            except OSError as e:
                logger.error(f"`OSError` while sending data: {e}")