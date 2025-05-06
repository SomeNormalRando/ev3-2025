# fix incorrect MIME types in Windows registry
import mimetypes
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, request, redirect, render_template, url_for
from flask_socketio import SocketIO, emit

from colour_detection_loop import start_colour_detection_loop
from connect_to_ev3 import connect_to_ev3_via_bluetooth_socket

from config import SERVER_RUN_PARAMS, CONNECT_TO_EV3, EVNAME_SEND_DEFAULT_HSV_COLOURS, RED1_LOWER, RED1_UPPER, RED2_LOWER, RED2_UPPER, BLUE_LOWER, BLUE_UPPER, BLUETOOTH_LOGGER_LEVEL, SOCKETIO_LOGGER_LEVEL

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

@flask_app.route("/control/")
def r_c():
    return redirect(url_for("control"))


@flask_app.route("/")
def index():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /")
    return render_template("index.html")

@flask_app.route("/interface")
def interface():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /interface")
    return render_template("interface.html")

@flask_app.route("/control")
def control():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /control")
    return render_template("control.html")

@flask_app.route("/stream/operator")
def stream_operator():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /stream/operator")
    return render_template("stream/operator.html")

@flask_app.route("/stream/robot")
def stream_robot():
    logger.info(f"{request.environ["REMOTE_ADDR"]} connected to /stream/robot")
    return render_template("stream/robot.html")

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

list = [
    "WEBRTC-ready-from-robot",
    "WEBRTC-bye-from-robot",
    "WEBRTC-ready-from-operator",
    "WEBRTC-bye-from-operator",

    "WEBRTC-offer-from-robot",
    "WEBRTC-answer-from-robot",
    "WEBRTC-candidate-from-robot",

    "WEBRTC-offer-from-operator",
    "WEBRTC-answer-from-operator",
    "WEBRTC-candidate-from-operator",
]
def create_webrtc_handler(evname):
    def handle_webrtc_event(*args):
        emit(evname, *args, broadcast = True, include_self = False)
        print(evname)
    return handle_webrtc_event
for evname in list:
    print(evname)
    socketio_app.on_event(evname, create_webrtc_handler(evname))

if (CONNECT_TO_EV3 is True):
    connect_to_ev3_via_bluetooth_socket(flask_app, socketio_app)
else:
    bl_logger.info(f"starting server without Bluetooth...")

    executor = ThreadPoolExecutor(max_workers=2)
    future = executor.submit(start_colour_detection_loop, socketio_app, None)

    print()
    future2 = executor.submit(socketio_app.run, app=flask_app, **SERVER_RUN_PARAMS)

    for f in as_completed([future, future2]):
        logger.error(f"`future` returned result: {f.result()}")