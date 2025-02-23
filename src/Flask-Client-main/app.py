import json
import base64
import os
from flask import Flask
from flask_socketio import SocketIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from headers.encrypt_functions import AESCipher, RSACipher
app = Flask(__name__)


# @app.route('/')
# def index():
#     return app.send_static_file('index.html')

# if __name__ == '__main__':
#     socketio.run(app, host='localhost', port=4000)


'''
NOT GONNA USE FLASK FOR CLIENT
'''