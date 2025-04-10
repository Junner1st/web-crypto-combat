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
def handle_register(data):
    rsa_key = data.get("rsa_key")

    logging.info(f"[register] Client {request.sid} registered with RSA key.")

    # Broadcast this client's RSA key to all others
    logging.debug(f"Current clients: {clients}")
    for sid in clients:
        if sid != request.sid:
            emit("receive_rsa_key", {"sid": request.sid, "rsa_key": rsa_key}, to=sid)
            logging.info(f"[emit] Sending RSA key to {sid}")

@socketio.on("send_aes_to_newcomer")
def handle_send_encrypted_aes(data):
    to_sid = data.get("target_sid")
    encrypted_aes = data.get("encrypted_aes")
    if to_sid in clients:
        emit("receive_aes_key", {"encrypted_aes": encrypted_aes}, to=to_sid)
        logging.info(f"[emit] Sending AES key to {to_sid}")
    else:
        logging.warning(f"Target client {to_sid} not found.")

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
        iv = payload_dict["iv"]
        logging.debug(f"Message: {message}")
        logging.debug(f"IV: {iv}")
    except (json.JSONDecodeError, KeyError) as e:
        logging.error("Invalid payload:", e)
        return
    
    emit("receive_message", {"sender": request.sid, "message": message, "iv": iv}, broadcast=True)
    logging.info(f"[emit] Broadcasting the message from {request.sid}")


if __name__ == "__main__":
    socketio.run(app, port=5055)
