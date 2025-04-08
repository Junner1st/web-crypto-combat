from flask import Flask, render_template, request
from flask_socketio import SocketIO
from include.crypt_functions import AESCipher, RSACipher
import logging
import base64
import eventlet


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


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)


clients = []

reply_count_PUBLIC = 0

reply_clients_list_single = []

@socketio.on("client_request_join")
def join_client():
    clients.append(request.sid)
    logger.info(f"[joined] {request.sid} joined the server.")
    for sid in clients:
        socketio.emit("server_sent_message", {"message": "joined", "client_sid": str(request.sid)}, room=sid)



@socketio.on("client_reply_recieved_PUBLIC")
def listen_to_client_reply_ANY(data):
    global reply_count_PUBLIC
    logger.info(f"[message] Received message from {request.sid}")
    logger.info(f"[message] Received message:{data.get('message')}")
    reply_count += 1
    socketio.emit("server_sent_message", {"message": "recieved"}, room=request.sid)
    logger.info("[message] Sent acknowledgement to client.")

@socketio.on("client_request_forward_message_ANY")
def server_forward_message_to_client_ANY(data, sent_event="message"):
    global reply_count

    def forward_message():
        for client_sid in clients:
            if client_sid != request.sid:
                socketio.emit(sent_event, data, room=client_sid)
            logger.info(f"[{sent_event}] Forwarded message from {request.sid}")

    def collect_replies():
        eventlet.sleep(5)
        logger.info(f"[replies] Received {reply_count} checked replies.")
        reply_count = 0

    eventlet.spawn(forward_message)
    eventlet.spawn(collect_replies)
    

@socketio.on("client_reply_recieved_SINGLE")
def listen_to_client_reply_SINGLE(data):
    global reply_clients_list_single

    logger.info(f"[message] Received message from {request.sid}")
    logger.info(f"[message] Received message:{data.get('message')}")
    reply_clients_list_single.append(request.sid)
    socketio.emit("server_sent_message", {"message": "recieved"}, room=request.sid)
    logger.info("[message] Sent acknowledgement to client.")

@socketio.on("client_request_forward_message_SINGLE")
def server_forward_message_to_client_SINGLE(data, sent_event="message"):
    global reply_clients_list_single

    sid = data.sid

    def forward_message():
        socketio.emit(sent_event, data, room=sid)
        logger.info(f"[{sent_event}] Forwarded message to {request.sid}")

    def collect_replies():
        eventlet.sleep(5)
        if sid in reply_clients_list_single:
            logger.info(f"[replies] Received {sid} checked replies.")
        else:
            logger.info(f"[replies] Timeout for {sid} checked replies. [5s]")
    
    eventlet.spawn(forward_message)
    eventlet.spawn(collect_replies)



@app.route('/')
def index():
    return render_template("index.html")



# @socketio.on("client_broadcast_rsa_public")
# def broadcast_rsa_public():
    

# @socketio.on("client_request_rsa_public")
# def send_rsa_public():
#     socketio.emit(
#         "server_sent_rsa_public_key",
#         {"public_key": server_rsa_public.export_key().decode()}
#         room=request.sid
#     )

# @socketio.on("client_sent_aes_key")
# def receive_aes_key(data):
#     global aes_key
#     encrypted_aes_key = base64.b64decode(data.get("aes_key"))

#     cipher_rsa = rsa_entity.cipher
#     aes_key = cipher_rsa.decrypt(encrypted_aes_key)

#     logger.info(f"[key exchange] AES Key:{aes_key}")
    

# @socketio.on("client_sent_message")
# def handle_encrypted_message(data):
#     global aes_key
#     global aes_iv
#     raw_message = data.get("message")
#     logger.info(f"[client_sent_message] Received raw message:{raw_message}")

#     ''' sent status to client '''
#     socketio.emit("server_sent_message", {"message": "recieved"})
#     logger.info("[message] Sent acknowledgement to client.")

#     ''' extract the initialization vector; before ":" '''
#     aes_iv = base64.b64decode(raw_message.split(":")[0])
#     aes_encrypted_message = raw_message.split(":")[1]
#     # aes_encrypted_message = aes_encrypted_message

#     logger.info(f"[crypt] Received AES IV:{aes_iv}")
#     logger.info(f"[message] Received AES encrypted message:{aes_encrypted_message}")

#     ''' decrypt the message '''
#     aes_entity.set_cipher(
#         key=aes_key,
#         iv=aes_iv
#     )
#     decrypted_message = aes_entity.decrypt_aes(aes_encrypted_message)

#     logger.info(f"[crypt] Received message:{decrypted_message}")


if __name__ == "__main__":
    logger.info("[server] Server started")
    socketio.run(app, host="localhost", port=5055, debug=True)
