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

from config import VIDEO_CAPTURE_DEVICE_INDEX, SOCKETIO_EVENT_NAME, SEND_TO_EV3_EVERY

def ndarray_to_b64(ndarray: numpy.typing.NDArray):
    return base64.b64encode(ndarray.tobytes()).decode()


def colour_detection_loop(socketio_app: flask_socketio.SocketIO, client_sock: socket.socket):
# def colour_detection_loop(socketio_app: flask_socketio.SocketIO):
    capture = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE_INDEX)

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

        (processed_frame, red_detected_objects) = detect_colour_and_draw(raw_frame, midpoint_x)

        (retval, jpg_image) = cv2.imencode(".jpg", processed_frame)

        if retval is False:
            logger.warning("image encoding unsuccessful, skipping frame")
            continue

        socketio_app.emit(SOCKETIO_EVENT_NAME, {    
            "b64ImageData": ndarray_to_b64(jpg_image),
            "redDetectedObjects": red_detected_objects,
        })


        if (now - last) < SEND_TO_EV3_EVERY:
            continue

        last = now
        try:
            client_sock.sendall(stringify_json(red_detected_objects).encode())
        except OSError as e:
            logger.error(f"`OSError` while sending data: {e}")