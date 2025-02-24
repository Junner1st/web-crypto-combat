import json
import base64
import os
from flask import Flask
from flask_socketio import SocketIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from include.crypt_functions import AESCipher, RSACipher

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

cipher = AESCipher()

@socketio.on("encrypt_message")
def handle_encrypt(data):
    """ 處理客戶端傳來的訊息並加密 """
    plaintext = data.get("message", "")
    encrypted = cipher.encrypt_aes(plaintext)

    print(f"[加密] 訊息: {plaintext} -> {encrypted}") # 終端輸出日誌
    
    socketio.emit("encrypted_response", {"encrypted": encrypted}) # 回傳加密結果

@socketio.on("decrypt_message")
def handle_decrypt(data):
    """ 處理客戶端請求解密 """
    encrypted_text = data.get("encrypted", "")
    try:
        decrypted = cipher.decrypt_aes(encrypted_text)

        # 終端輸出日誌
        print(f"[解密] 訊息: {encrypted_text} -> {decrypted}")

        # 回傳解密結果
        socketio.emit("decrypted_response", {"decrypted": decrypted})
    except Exception as e:
        print("[解密錯誤]", str(e))
        socketio.emit("decryption_error", {"error": "無法解密該訊息"})

if __name__ == "__main__":
    print("[伺服器啟動中...]")
    socketio.run(app, host="localhost", port=5000, debug=True)
