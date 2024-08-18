# fix incorrect MIME types in Windows registry
import mimetypes
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

from flask import Flask, request, redirect, render_template, url_for
from flask_socketio import SocketIO, emit

import socket
from colour_detection_loop import colour_detection_loop
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import SERVER_RUN_PARAMS, BLUETOOTH_ADDRESS, BLUETOOTH_CHANNEL, do_bluetooth, EVNAME_SEND_DEFAULT_HSV_COLOURS, RED1_LOWER, RED1_UPPER, RED2_LOWER, RED2_UPPER, BLUE_LOWER, BLUE_UPPER, BLUETOOTH_LOGGER_LEVEL, SOCKETIO_LOGGER_LEVEL

import logging
logging.basicConfig(
    format = "\x1b[30m[%(asctime)s \x1b[33m%(name)s\x1b[30m %(levelname)s] \x1b[97m%(message)s\x1b[0m", 
    datefmt = "%H:%M:%S",
    level = logging.DEBUG
)
logger = logging.getLogger(__name__)
bl_logger = logging.getLogger("bluetooth")
bl_logger.setLevel(BLUETOOTH_LOGGER_LEVEL)
socketio_logger = logging.getLogger("socket.io")
socketio_logger.setLevel(SOCKETIO_LOGGER_LEVEL)

# werkzeug logs all incoming connections at level logging.INFO, so set level to logging.ERROR to disable it
werkzeug_logger = logging.getLogger("werkzeug")
# werkzeug_logger.setLevel(logging.ERROR)


flask_app = Flask(__name__, static_folder="static", template_folder="templates")
socketio_app = SocketIO(flask_app)

# region ROUTES
# redirects
@flask_app.route("/interface/")
def r_i():
    return redirect(url_for("interface"))

@flask_app.route("/camera/")
def r_c():
    return redirect(url_for("camera"))


@flask_app.route("/")
def index():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /")
    return render_template("index.html")

@flask_app.route("/interface")
def interface():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /interface")
    return render_template("interface.html")

@flask_app.route("/gyro")
def gyro():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /gyro")
    return render_template("gyro.html")

@flask_app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.ico"))
# endregion

@socketio_app.on("connect")
def handle_connect():
    socketio_logger.info("connection received")
    emit(EVNAME_SEND_DEFAULT_HSV_COLOURS, {
        "RED1_LOWER": RED1_LOWER.tolist(),
        "RED1_UPPER": RED1_UPPER.tolist(),
        "RED2_LOWER": RED2_LOWER.tolist(),
        "RED2_UPPER": RED2_UPPER.tolist(),
        "BLUE_LOWER": BLUE_LOWER.tolist(),
        "BLUE_UPPER": BLUE_UPPER.tolist(),
    }, callback = (lambda _: socketio_logger.info("sent default HSV colours to client")))

if (do_bluetooth is False):
    bl_logger.info(f"starting server without Bluetooth...")

    executor = ThreadPoolExecutor(max_workers=2)
    future = executor.submit(colour_detection_loop, socketio_app)

    print()
    future2 = executor.submit(socketio_app.run, app=flask_app, **SERVER_RUN_PARAMS)

    for f in as_completed([future, future2]):
        logger.error(f"`future` returned result: {f.result()}")

# executes if do_bluetooth is True
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

    executor = ThreadPoolExecutor(max_workers=2)
    future = executor.submit(colour_detection_loop, socketio_app, client_sock)

    print()
    future2 = executor.submit(socketio_app.run, app=flask_app, **SERVER_RUN_PARAMS)

    for f in as_completed([future, future2]):
        logger.error(f"`future` returned result: {f.result()}")
