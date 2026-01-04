from flask import Flask, render_template
from flask_socketio import SocketIO
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent

app = Flask(__name__)
socketio = SocketIO(app)

# O ID de usuário do TikTok a ser conectado
TIKTOK_USER_ID = "@billieeilish"

@app.route('/')
def index():
    return render_template('index.html')

def on_connect(event: ConnectEvent):
    print(f"Conectado à live de {TIKTOK_USER_ID}")
    socketio.emit('status', {'type': 'connect', 'message': f"Conectado à live de {event.unique_id}"})

def on_comment(event: CommentEvent):
    print(f"{event.user.nickname}: {event.comment}")
    socketio.emit('comment', {'nickname': event.user.nickname, 'comment': event.comment})

def start_tiktok_listener():
    client = TikTokLiveClient(unique_id=TIKTOK_USER_ID)
    client.add_listener("connect", on_connect)
    client.add_listener("comment", on_comment)
    client.run_in_async()

if __name__ == '__main__':
    socketio.start_background_task(start_tiktok_listener)
    socketio.run(app, host='0.0.0.0', port=5000)