# fix incorrect MIME types in Windows registry
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from flask import Flask, redirect, render_template, url_for
from flask_socketio import SocketIO

import socket
from colour_detection_loop import colour_detection_loop
from concurrent.futures import ThreadPoolExecutor

import logging
logging.basicConfig(
    format="\x1b[30m[%(asctime)s \x1b[33m%(name)s\x1b[30m %(levelname)s] \x1b[97m%(message)s\x1b[0m", 
    datefmt="%H:%M:%S",
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)
bl_logger = logging.getLogger("bluetooth")

from config import SERVER_PORT, BLUETOOTH_ADDRESS, BLUETOOTH_CHANNEL, do_bluetooth

flask_app = Flask(__name__, static_folder="static", template_folder="templates")
socketio_app = SocketIO(flask_app)

run_params = {
    "app": flask_app,
    "host": "0.0.0.0",
    "port": SERVER_PORT,
    "debug": True,
    "use_reloader": False,
    "log_output": True,
    # generate self-signed SSL certificate (so that getUserMedia isn't auto-disabled in browsers)
    # "ssl_context": "adhoc"
}

# region ROUTES
# redirects
@flask_app.route('/interface/')
def r_i():
    return redirect(url_for("interface"))

@flask_app.route('/camera/')
def r_c():
    return redirect(url_for("camera"))


@flask_app.route("/")
def index():
    return render_template("index.html")

@flask_app.route("/interface")
def interface():
    return render_template("interface.html")

@flask_app.route("/camera")
def camera():
    return render_template("camera.html")
# endregion

# region colour detection
if (do_bluetooth is False):
    bl_logger.info(f"starting server without Bluetooth...")

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(colour_detection_loop, socketio_app)

    print()
    socketio_app.run(**run_params)

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

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(colour_detection_loop, socketio_app, client_sock)

    if __name__ == "__main__":
        print()
        socketio_app.run(**run_params)
# endregion
