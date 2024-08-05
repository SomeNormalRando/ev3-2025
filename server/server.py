import logging
logging.basicConfig(
    format="\x1b[30m[%(asctime)s \x1b[33m%(levelname)s\x1b[30m] \x1b[34m%(message)s\x1b[0m", 
    datefmt="%H:%M:%S",
    level=logging.DEBUG
)

# fix incorrect MIME types in Windows registry
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from flask import Flask, redirect, render_template, url_for
from flask_socketio import SocketIO

import socket
from colour_detection_loop import colour_detection_loop
from concurrent.futures import ThreadPoolExecutor


PORT = 8000
# address of the bluetooth device of this computer (the one you are using right now)
# JC's address: D8:12:65:88:74:74
BLUETOOTH_ADDRESS = "60:f2:62:a9:d8:cc" 
CHANNEL = 5 # random number

do_bluetooth = True

flask_app = Flask(__name__, static_folder="static", template_folder="templates")
socketio_app = SocketIO(flask_app)

run_params = {
    "app": flask_app,
    "host": "0.0.0.0",
    "port": PORT,
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
    logging.info(f"Starting server without Bluetooth.\n")

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(colour_detection_loop, socketio_app)

    socketio_app.run(**run_params)

with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as server_sock:
    logging.info(f"[Bluetooth] Created server socket {server_sock}.")

    server_sock.bind((BLUETOOTH_ADDRESS, CHANNEL))
    server_sock.listen(1)

    logging.info("[Bluetooth] Waiting for socket connection from client (EV3)...")

    client_sock, address = server_sock.accept()

    logging.info(f"[Bluetooth] Accepted connection from client socket.")
    logging.debug(f"\x1b[30m`client_sock`: {client_sock}, address {address}")
    logging.debug(f"\x1b[30m`server_sock`: {server_sock}")

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(colour_detection_loop, socketio_app, client_sock)

    if __name__ == "__main__":
        socketio_app.run(**run_params)
# endregion
