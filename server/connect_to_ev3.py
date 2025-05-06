import socket
from json import dumps as stringify_json
from concurrent.futures import ThreadPoolExecutor, as_completed

import logging
logger = logging.getLogger(__name__)
bl_logger = logging.getLogger("bluetooth")
socketio_logger = logging.getLogger("socket.io")

from colour_detection_loop import start_colour_detection_loop

from config import SERVER_RUN_PARAMS, BLUETOOTH_ADDRESS, BLUETOOTH_CHANNEL, EVNAME_RECEIVE_MOVEMENT_COMMAND, EVNAME_RECEIVE_FUNNEL_COMMAND, EVNAME_RECEIVE_AUTO_MODE_COMMAND

def connect_to_ev3_via_bluetooth_socket(flask_app, socketio_app):
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as server_sock:
        bl_logger.info(f"created server socket")
        bl_logger.debug(f"\x1b[30m`server_sock`: {server_sock}")

        server_sock.bind((BLUETOOTH_ADDRESS, BLUETOOTH_CHANNEL))
        server_sock.listen(1)

        bl_logger.info("waiting for socket connection from client (EV3)...")

        client_sock, address = server_sock.accept()

        bl_logger.info(f"accepted connection from client socket")
        bl_logger.debug(f"\x1b[30m`client_sock`: {client_sock}, address {address}")
        bl_logger.debug(f"\x1b[30m`server_sock`: {server_sock}")

        # robot remote control from the web interface
        @socketio_app.on(EVNAME_RECEIVE_MOVEMENT_COMMAND)
        def receive_movement_command(movement_direction, movement_speed):
            socketio_logger.info("receive_movement_command: direction {} & speed {}".format(movement_direction, movement_speed))
            client_sock.sendall(stringify_json({
                "type": "MOVEMENT",
                "direction": movement_direction,
                "speed": movement_speed
            }).encode())

        @socketio_app.on(EVNAME_RECEIVE_FUNNEL_COMMAND)
        def receive_funnel_command(command):
            socketio_logger.info("receive_funnel_command: command {}".format(command))
            client_sock.sendall(stringify_json({
                "type": "FUNNEL",
                "command": command
            }).encode())

        @socketio_app.on(EVNAME_RECEIVE_AUTO_MODE_COMMAND)
        def receive_auto_mode_command(command):
            socketio_logger.info("receive_auto_mode_command: command {}".format(command))
            client_sock.sendall(stringify_json({
                "type": "AUTO_MODE",
                "command": command
            }).encode())

        executor = ThreadPoolExecutor(max_workers=2)
        future = executor.submit(start_colour_detection_loop, socketio_app, client_sock)

        print()
        future2 = executor.submit(socketio_app.run, app=flask_app, **SERVER_RUN_PARAMS)

        for f in as_completed([future, future2]):
            logger.error(f"`future` returned result: {f.result()}")