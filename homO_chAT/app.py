from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# 定義聊天室房間名稱，方便管理
ROOM = "main_chat_room"

@app.route('/')
def index():
    # 初始頁面，用戶選擇身分 (僅限 Alice 與 Bob)
    return render_template('index.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    # 簡單驗證，只接受 Alice 或 Bob
    if not username or username not in ['Alice', 'Bob']:
        return "請使用有效的用戶名稱: Alice 或 Bob", 400
    session['username'] = username
    return render_template('chat.html', username=username)

# 客戶端進入聊天室時通知伺服器加入同一房間
@socketio.on('join')
def handle_join(data):
    username = session.get('username', '匿名用戶')
    join_room(ROOM)
    emit('status', {'msg': f'{username} 已進入聊天室'}, room=ROOM)

# 處理發送訊息事件，將訊息傳送至同一個房間內的所有人
@socketio.on('text')
def handle_text(data):
    username = session.get('username', '匿名用戶')
    msg = data['msg']
    emit('message', {'msg': f'{username}: {msg}'}, room=ROOM)

# 使用者離線時通知房間內的其他人
@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username', '匿名用戶')
    leave_room(ROOM)
    emit('status', {'msg': f'{username} 已離開聊天室'}, room=ROOM)

if __name__ == '__main__':
    socketio.run(app, debug=True)
