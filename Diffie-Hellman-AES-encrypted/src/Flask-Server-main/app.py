from flask import Flask, render_template
from flask_socketio import SocketIO
from include.crypt_functions import AESCipher, RSACipher
import logging
import base64


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)

rsa_entity = RSACipher()
server_rsa_private = rsa_entity.private_key
server_rsa_public = rsa_entity.public_key

aes_entity = AESCipher()
aes_key = None
aes_iv = None

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("client_request_rsa_public")
def send_rsa_public():
    socketio.emit("server_sent_rsa_public_key", {"public_key": server_rsa_public.export_key().decode()})

@socketio.on("client_sent_aes_key")
def receive_aes_key(data):
    global aes_key
    encrypted_aes_key = base64.b64decode(data.get("aes_key"))

    cipher_rsa = rsa_entity.cipher
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)

    logger.info(f"[key exchange] AES Key:{aes_key}")
    

@socketio.on("client_sent_message")
def handle_encrypted_message(data):
    global aes_key
    global aes_iv
    raw_message = data.get("message")
    logger.info(f"[message] Received raw message:{raw_message}")

    ''' sent status to client '''
    socketio.emit("server_sent_message", {"message": "recieved"})
    logger.info("[message] Sent acknowledgement to client.")

    ''' extract the initialization vector; before ":" '''
    aes_iv = base64.b64decode(raw_message.split(":")[0])
    aes_encrypted_message = raw_message.split(":")[1]
    # aes_encrypted_message = aes_encrypted_message

    logger.info(f"[crypt] Received AES IV:{aes_iv}")
    logger.info(f"[message] Received AES encrypted message:{aes_encrypted_message}")

    ''' decrypt the message '''
    aes_entity.set_cipher(
        key=aes_key,
        iv=aes_iv
    )
    decrypted_message = aes_entity.decrypt_aes(aes_encrypted_message)

    logger.info(f"[crypt] Received message:{decrypted_message}")



if __name__ == "__main__":
    logger.info("[server] Server started")
    socketio.run(app, host="localhost", port=5055, debug=True)
