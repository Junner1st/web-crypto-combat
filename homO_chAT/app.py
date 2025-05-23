from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from threading import Lock

# 引入加密模組，可輕易替換不同實作
from encryption import encrypt_algo

app = Flask(__name__)
app.config['SECRET_KEY'] = '1145141919810'
socketio = SocketIO(app)

# 定義聊天室與監控室名稱
CHAT_ROOM = "chat_room"
MONITOR_ROOM = "monitor_room"

enc_objects = {}
# 全局鎖，用於同步操作 enc_objects
enc_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    if not username or username not in ['Alice', 'Bob']:
        return "請使用有效的用戶名稱：Alice 或 Bob", 403
    session['username'] = username
    return render_template('chat.html', username=username)

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@socketio.on('join_chat')
def handle_join_chat(data):
    username = session.get('username', 'unknown_user')
    join_room(CHAT_ROOM)
    # 通知聊天室與監控端
    emit('status', {'msg': f'{username} 進入聊天室'}, room=CHAT_ROOM)
    emit('monitor_info', {'msg': f'{username} 加入聊天室'}, room=MONITOR_ROOM)

@socketio.on('join_monitor')
def handle_join_monitor(data):
    join_room(MONITOR_ROOM)
    emit('monitor_info', {'msg': '監控端已連線'}, room=MONITOR_ROOM)

@socketio.on('start_key_exchange')
def handle_key_exchange(data):
    with enc_lock:
        username = session.get('username', 'unknown_user')

        # 防止使用者重複發起金鑰交換
        if username in enc_objects:
            emit('status', {'msg': f'{username} 正在金鑰交換中，不可重複發起'}, room=request.sid)
            return
        
        emit('status', {'msg': f'{username} 開始金鑰交換'}, room=CHAT_ROOM)
        emit('monitor_info', {'msg': f'[KEY_EXCHANGE] {username} 開始金鑰交換'}, room=MONITOR_ROOM)

        # 產生金鑰，並儲存加密演算法的實例
        enc_objects[username] = encrypt_algo()
        enc_objects[username].generate_keys()
        public_key_info = enc_objects[username].get_public_key_info()
        private_key_info = enc_objects[username].get_private_key_info()

        # 告知用戶端產生金鑰資訊
        emit('status', {'msg': f'{username} 產生 public_key: {public_key_info}'}, room=request.sid)
        emit('status', {'msg': f'{username} 產生 private_key: {private_key_info}'}, room=request.sid)

        # 向聊天室和監控室送出發佈公鑰消息
        emit('status', {'msg': f'{username} 發出公鑰: {public_key_info}'}, room=CHAT_ROOM)
        emit('monitor_info', {'msg': f'[KEY_EXCHANGE] {username} 發出公鑰: {public_key_info}'}, room=MONITOR_ROOM)

        # 若只有一位使用者，則等待另一方加入
        if len(enc_objects) == 1:
            emit('status', {'msg': f'{username} 等待另一方…'}, room=CHAT_ROOM)
            emit('monitor_info', {'msg': f'[KEY_EXCHANGE] {username} 等待另一方…'}, room=MONITOR_ROOM)
            return

        # 若已有其他使用者，進行金鑰交換
        # 使用列表推導式取得非當前使用者的名稱
        other_users = [user for user in enc_objects if user != username]
        if not other_users:
            emit('status', {'msg': f'{username} 尚無其他使用者進行金鑰交換'}, room=request.sid)
            return
        other_user = other_users[0]
        other_public_key_info = enc_objects[other_user].get_public_key_info()

        # 將對方的公鑰交換給當前用戶
        emit('status', {'msg': f'{username} 接收公鑰: {other_public_key_info}'}, room=CHAT_ROOM)
        emit('monitor_info', {'msg': f'[KEY_EXCHANGE] {username} 接收公鑰: {other_public_key_info}'}, room=MONITOR_ROOM)
        enc_objects[username].exchange_keys(enc_objects[other_user].public_key)

        # 將當前用戶的公鑰交換給對方
        emit('status', {'msg': f'{other_user} 接收公鑰: {public_key_info}'}, room=CHAT_ROOM)
        emit('monitor_info', {'msg': f'[KEY_EXCHANGE] {other_user} 接收公鑰: {public_key_info}'}, room=MONITOR_ROOM)
        enc_objects[other_user].exchange_keys(enc_objects[username].public_key)

        emit('status', {'msg': '金鑰交換完成，開始對話'}, room=CHAT_ROOM)

@socketio.on('chat_message')
def handle_chat_message(data):
    username = session.get('username', 'unknown_user')
    msg = data.get('msg', '')
    
    with enc_lock:
        if len(enc_objects) < 2:
            emit('status', {'msg': '尚未完成金鑰交換，請先生成金鑰'}, room=request.sid)
            return
        
        other_user = [user for user in enc_objects if user != username][0]
    
        plaintext = msg.encode('utf-8')
        ciphertext = enc_objects[username].encrypt(plaintext)
        recovered_text = enc_objects[other_user].decrypt(ciphertext).decode('utf-8')
        
    emit('message', {'msg': f'{username}: {recovered_text}'}, room=CHAT_ROOM)
    emit('monitor_info', {'msg': f'{username} (encrypted): {ciphertext.hex()}'}, room=MONITOR_ROOM)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username', 'unknown_user')
    with enc_lock:
        enc_objects.pop(username, None)
    leave_room(CHAT_ROOM)
    leave_room(MONITOR_ROOM)
    emit('status', {'msg': f'{username} 離開聊天室'}, room=CHAT_ROOM)
    emit('monitor_info', {'msg': f'{username} 離開系統'}, room=MONITOR_ROOM)

if __name__ == '__main__':
    socketio.run(app, debug=True)