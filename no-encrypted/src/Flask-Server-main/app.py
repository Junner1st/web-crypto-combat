from flask import Flask, render_template
from flask_socketio import SocketIO
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
import base64
import os
from include.crypt_functions import AESCipher, RSACipher

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("client_sent_message")
def handle_encrypted_message(data):
    raw_message = data.get("message")
    print(f"message recieved: {raw_message}")
    socketio.emit("server_sent_message", {"message": "recieved"})

if __name__ == "__main__":
    print("[server started...]")
    socketio.run(app, host="localhost", port=5000, debug=True)
