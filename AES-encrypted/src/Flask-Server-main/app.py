from flask import Flask, render_template
from flask_socketio import SocketIO
from include.crypt_functions import AESCipher
import logging
import base64


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(filename='./log.csv', level=logging.INFO, format='%(asctime)s, %(levelname)s, %(message)s')
logger = logging.getLogger(__name__)

aes_entity = AESCipher()
aes_key = None

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("client_sent_aes_key")
def receive_aes_key(data):
    global aes_key
    aes_key = base64.b64decode(data.get("aes_key"))
    

@socketio.on("client_sent_message")
def handle_encrypted_message(data):
    raw_message = data.get("message")
    print(f"message received: {raw_message}")

    ''' sent status to client '''
    socketio.emit("server_sent_message", {"message": "recieved"})
    logger.info("Sent acknowledgement to client.")

    ''' extract the initialization vector; before ":" '''
    aes_iv = base64.b64decode(raw_message.split(":")[0])
    aes_encrypted_message = raw_message.split(":")[1]

    ''' decrypt the message '''
    aes_entity.set_cipher(
        key=aes_key,
        iv=aes_iv
    )
    decrypted_message = aes_entity.decrypt_aes(aes_encrypted_message)

    logger.info(f"Received message: {decrypted_message}")
    print(f"decrypted message: {decrypted_message}")



if __name__ == "__main__":
    print("[server started...]")
    logger.info("[server started...]")
    socketio.run(app, host="localhost", port=5000, debug=True)
