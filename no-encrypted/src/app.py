from flask import Flask, render_template
from flask_socketio import SocketIO
from Crypto.Util.Padding import pad, unpad
from include.crypt_functions import AESCipher, RSACipher
import logging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(filename='./log.csv', level=logging.INFO, format='%(asctime)s, %(levelname)s, %(message)s')
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("client_sent_message")
def handle_message(data):
    raw_message = data.get("message")
    print(f"message received: {raw_message}")
    logger.info(f"Received message: {raw_message}")
    socketio.emit("server_sent_message", {"message": "recieved"})
    logger.info("Sent acknowledgement to client.")

if __name__ == "__main__":
    print("[server started...]")
    logger.info("[server started...]")
    socketio.run(app, host="localhost", port=5000, debug=True)