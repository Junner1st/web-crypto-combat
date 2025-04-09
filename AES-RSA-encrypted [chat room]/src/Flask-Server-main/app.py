'''
character: c_i, server
js FUNCTION any_client_publish_rsa_key() -> INTEGER {
    1. if (ANY c_i) join, c_i publish and broadcast its own rsa public key to (ANY client) ∩ (not self);
    2. SOCKET.ON listen_to_checked_recieved_PUBLIC() -> INTEGER;
    
    RETURN 2.
}

js SOCKET.ON any_client_listen_rsa_public() -> VOID {
    1. SOCKET.ON listen to (ANY c_i) ( "rsa_public" );
    2. CALL sent_rsa_encrypted_aes_key(*) -> BOOLEAN;
}

js FUNCTION sent_rsa_encrypted_aes_key( rsaPublic/rsa entity, aesKey ) -> BOOLEAN {
    1. EMIT rsaPublic_encrypt( aesKey );
    2. SOCKET.ON listen_to_checked_recieved_SINGLE() -> BOOLEAN;

    RETURN 2.
}

js FUNCTION client_decrypt_aes_key( rsaPrivate/rsa entity, encrypted_aesKey ) -> BOOLEAN {
    1. decrypt encrypted_aesKey;
    
    return 1. : decrypt success or not 
}

js FUNCTION client_message_to_server(STRING text) -> BOOLEAN {
    1. EMIT text to server;
    2. SOCKET.ON server_reply_recieved() -> BOOLEAN;

    RETURN 2. 
}

python FUNCTION server_forward_message_to_client_ANY( STRING text ) -> INREGER {
    1. SOCKET.ON server_forward_message() to (ANY client) ∩ (not self);
    2. SOCKET.ON listen_to_client_reply_recieved_PUBLIC() -> INREGER;

    RETURN 2. 
}

python FUNCTION server_forward_message_to_client_SINGLE( STRING text, STRING sid ) -> BOOLEAN {
    1. SOCKET.ON server_forward_message() to c_{sid};
    2. SOCKET.ON listen_to_client_reply_recieved_SINGLE() -> BOOLEAN;

    RETURN 2. 
}
'''

from flask import Flask, request
from flask_socketio import SocketIO, emit, send
from flask_cors import CORS
import logging
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

clients = []

@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")
    clients.append(request.sid)

    user_list = [sid for sid in clients if sid != request.sid]
    emit("connect_ack", {"user_list": user_list})
    # print(f"Connected clients: {user_list}")

@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in clients:
        clients.remove(request.sid)
        emit("user_left", {"sid": request.sid}, broadcast=True)

@socketio.on("register")
def handle_register(data):
    rsa_key = data.get("rsa_key")

    print(f"Client {request.sid} registered with RSA key.")


    # Broadcast this client's RSA key to all others
    print(f"current clients: {clients}")
    for sid in clients:
        if sid != request.sid:
            print(f"Sending RSA key to {sid}")
            emit("receive_rsa_key", {"sid": request.sid, "rsa_key": rsa_key}, to=sid)

@socketio.on("send_aes_to_newcomer")
def handle_send_encrypted_aes(data):
    to_sid = data.get("target_sid")
    encrypted_aes = data.get("encrypted_aes")
    if to_sid in clients:
        print(f"Sending AES key to {to_sid}")
        emit("receive_aes_key", {"encrypted_aes": encrypted_aes}, to=to_sid)
    else:
        print(f"Target client {to_sid} not found.")

@socketio.on("send_message")
def handle_send_message(data):
    payload = data.get("payload")
    print(f"Received payload: {payload}")
    if payload is None:
        print("Invalid payload: payload is None")
        return
    try:
        payload_dict = json.loads(payload)
        message = payload_dict["data"]
        iv = payload_dict["iv"]
        print(f"Message: {message}")
        print(f"IV: {iv}")
    except (json.JSONDecodeError, KeyError) as e:
        print("Invalid payload:", e)
        return
    

    print(f"Received message: {message} from {request.sid}")
    emit("receive_message", {"sender": request.sid, "message": message, "iv": iv}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, port=5055)
