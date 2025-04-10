from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

clients = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

@app.route("/")
def index():
    return "Server is running."

@socketio.on("connect")
def handle_connect():
    logging.info(f"[connect] Client connected: {request.sid}")
    clients.append(request.sid)

    user_list = [sid for sid in clients if sid != request.sid]
    emit("connect_ack", {"user_list": user_list})
    logging.info(f"[emit] Sending user list to {request.sid}")
    logging.debug(f"User list: {user_list}")

@socketio.on("disconnect")
def handle_disconnect():
    logging.info(f"[disconnect] Client disconnected: {request.sid}")
    if request.sid in clients:
        clients.remove(request.sid)
        logging.debug(f"Client {request.sid} removed from client list.")
        # emit("user_left", {"sid": request.sid}, broadcast=True)

@socketio.on("register")
def handle_register():
    logging.info(f"[register] Client {request.sid} registered.")


@socketio.on("send_message")
def handle_send_message(data):
    payload = data.get("payload")
    logging.debug(f"Received payload: {payload}")
    if payload is None:
        print("[Invalid payload] payload is None")
        logging.warning("[Invalid payload] payload is None")
        return
    try:
        payload_dict = json.loads(payload)
        message = payload_dict["data"]
        logging.debug(f"Message: {message}")
    except (json.JSONDecodeError, KeyError) as e:
        logging.error("Invalid payload:", e)
        return
    
    emit("receive_message", {"sender": request.sid, "message": message}, broadcast=True)
    logging.info(f"[emit] Broadcasting the message from {request.sid}")


if __name__ == "__main__":
    socketio.run(app, port=5055)
