from flask import Flask, render_template
from flask_socketio import SocketIO
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 產生 RSA 公私鑰
rsa_key = RSA.generate(2048)
server_rsa_private = rsa_key.export_key()
server_rsa_public = rsa_key.publickey().export_key()
server_rsa_public_key = RSA.import_key(server_rsa_public)
print(f"RAW RSA PUBLIC KEY:\n{server_rsa_public.decode()}")
print(f"🔑 伺服器 RSA 公鑰: e={hex(server_rsa_public_key.e)}\nn={hex(server_rsa_public_key.n)}")
print(f"🔑 伺服器 RSA 私鑰: d={hex(rsa_key.d)}\np={hex(rsa_key.p)},\nq={hex(rsa_key.q)}")

# AES 金鑰（初始化為 None，等待客戶端傳送加密版本）
AES_KEY = None
AES_IV = None

# def encrypt_aes(plain_text):
#     cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
#     padded_text = plain_text + (16 - len(plain_text) % 16) * ' '
#     encrypted = cipher.encrypt(padded_text.encode('utf-8'))
#     return base64.b64encode(encrypted).decode('utf-8')

# def decrypt_aes(encrypted_text):
#     cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
#     print(f"🔐 AES 解密: {base64.b64decode(encrypted_text)}")
#     decrypted = cipher.decrypt(base64.b64decode(encrypted_text))
#     return decrypted

# v2
# def decrypt_aes(encrypted_text):
#     # print(f"🔐 raw message {encrypted_text}")
#     aes_cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
#     base64Decoded = base64.b64decode(encrypted_text)
#     decrypted = aes_cipher.decrypt(base64Decoded)
#     # print(f"🔐 AES 解密 raw: {base64Decoded} | {len(base64Decoded)} | {decrypted}")

#     # 去除 PKCS7 填充
#     pad_len = decrypted[-1]  # 取得 padding 長度
#     # print(f"🔐 AES padding 長度: {pad_len}")
#     decrypted = decrypted[:-(pad_len)]
#     # print(f"🔐 AES padding 移除: {decrypted}")
#     decrypted = decrypted.decode()
#     # print(f"🔐 AES 解密: {decrypted}")

#     return decrypted

def decrypt_aes(encrypted_text):
    aes_cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    base64Decoded = base64.b64decode(encrypted_text)
    decrypted = aes_cipher.decrypt(base64Decoded)

    pad_len = decrypted[-1]  # 取得 padding 長度
    decrypted = decrypted[:-(pad_len)]
    decrypted = decrypted.decode()

    return decrypted


@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("request_rsa_public")
def send_rsa_public():
    """客戶端請求 RSA 公鑰"""
    print("📢 客戶端請求 RSA 公鑰")
    socketio.emit("rsa_public_key", {"public_key": server_rsa_public.decode()})

@socketio.on("send_encrypted_aes_key")
def receive_encrypted_aes(data):
    """接收加密後的 AES 金鑰"""
    global AES_KEY, AES_IV
    encrypted_aes_key = base64.b64decode(data.get("aes_key"))
    encrypted_aes_iv = base64.b64decode(data.get("aes_iv"))

    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(server_rsa_private))
    AES_KEY = cipher_rsa.decrypt(encrypted_aes_key)
    AES_IV = cipher_rsa.decrypt(encrypted_aes_iv)

    print(f"✅ AES 金鑰交換成功！AES_KEY: {AES_KEY.hex()}, AES_IV: {AES_IV.hex()}")
    socketio.emit("aes_key_exchange_success")

    

@socketio.on("encrypted_message")
def handle_encrypted_message(data):
    if AES_KEY is None:
        socketio.emit("encryption_error", {"error": "AES Key 未設定"})
        return
    message = data.get("message")
    raw_message = decrypt_aes(message)
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
