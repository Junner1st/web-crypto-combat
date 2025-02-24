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

rsa_entity = RSACipher()
server_rsa_private = rsa_entity.private_key
server_rsa_public = rsa_entity.public_key

# server_rsa_public_key = RSA.import_key(server_rsa_public)
# print(f"RAW RSA PUBLIC KEY:\n{server_rsa_public.decode()}")
# print(f"🔑 伺服器 RSA 公鑰: e={hex(server_rsa_public_key.e)}\nn={hex(server_rsa_public_key.n)}")
# print(f"🔑 伺服器 RSA 私鑰: d={hex(rsa_key.d)}\np={hex(rsa_key.p)},\nq={hex(rsa_key.q)}")

aes_entity = AESCipher()

# def encrypt_aes(plain_text):
#     cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
#     padded_text = plain_text + (16 - len(plain_text) % 16) * ' '
#     encrypted = cipher.encrypt(padded_text.encode('utf-8'))
#     return base64.b64encode(encrypted).decode('utf-8')


def decrypt_aes(encrypted_text):
    aes_cipher = AES.new(aes_entity.AES_KEY, AES.MODE_CBC, aes_entity.AES_IV)
    base64Decoded = base64.b64decode(encrypted_text)
    decrypted = aes_cipher.decrypt(base64Decoded)

    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len].decode()

    return decrypted



@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("request_rsa_public")
def send_rsa_public():
    """客戶端請求 RSA 公鑰"""
    print("📢 客戶端請求 RSA 公鑰")
    socketio.emit("rsa_public_key", {"public_key": server_rsa_public.export_key().decode()})

@socketio.on("send_encrypted_aes_key")
def receive_encrypted_aes_key(data):
    """接收加密後的 AES 金鑰"""
    global aes_entity
    
    encrypted_aes_key = base64.b64decode(data.get("aes_key"))
    encrypted_aes_iv = base64.b64decode(data.get("aes_iv"))

    cipher_rsa = rsa_entity.cipher
    aes_entity.set_cipher(cipher_rsa.decrypt(encrypted_aes_key), cipher_rsa.decrypt(encrypted_aes_iv))

    print(f"AES 金鑰交換成功！AES_KEY: {aes_entity.AES_KEY}, AES_IV: {aes_entity.AES_IV }")
    socketio.emit("aes_key_exchange_success")

    

@socketio.on("encrypted_message")
def handle_encrypted_message(data):
    if aes_entity.AES_KEY is None:
        socketio.emit("encryption_error", {"error": "AES Key 未設定"})
        return
    message = data.get("message")
    raw_message = aes_entity.decrypt_aes(message)
    # encrypted_msg = encrypt_aes(message)
    print(f"🔐 伺服器收到訊息: {raw_message}")
    # socketio.emit("encrypted_response", {"encrypted": encrypted_msg})

# @socketio.on("decrypt_message")
# def handle_decrypt(data):
#     """客戶端發送解密請求"""
#     if AES_KEY is None:
#         socketio.emit("decryption_error", {"error": "AES Key 未設定"})
#         return
#     encrypted_msg = data.get("encrypted")
#     try:
#         decrypted_msg = decrypt_aes(encrypted_msg)
#         print(f"🔓 伺服器解密訊息: {encrypted_msg} -> 解密: {decrypted_msg}")
#         socketio.emit("decrypted_response", {"decrypted": decrypted_msg})
#     except Exception as e:
#         socketio.emit("decryption_error", {"error": str(e)})

if __name__ == "__main__":
    print("[🚀 伺服器啟動...]")
    socketio.run(app, host="localhost", port=5000, debug=True)
