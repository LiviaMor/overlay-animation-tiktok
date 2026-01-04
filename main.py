import os
import asyncio
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, JoinEvent, CommentEvent

# Carrega secrets do Render ou .env local
secrets_path = "/etc/secrets/.env"
local_env_path = ".env"

env_file = secrets_path if os.path.exists(secrets_path) else local_env_path

if os.path.exists(env_file):
    print(f"Carregando variáveis de: {env_file}")
    with open(env_file, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
                print(f"  Carregado: {key.strip()}")
else:
    print(f"Arquivo .env não encontrado em: {env_file}")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurações via variáveis de ambiente
TIKTOK_USER_ID = os.getenv("TIKTOK_USER_ID")

if not TIKTOK_USER_ID:
    raise ValueError("TIKTOK_USER_ID não configurado! Defina no .env ou variáveis de ambiente.")

# Cria o cliente TikTok
client = TikTokLiveClient(unique_id=TIKTOK_USER_ID)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Conectado à live de {event.unique_id}")
    socketio.emit('status', {'type': 'connect', 'message': f"Conectado à live de {event.unique_id}"})

@client.on(JoinEvent)
async def on_join(event: JoinEvent):
    """Quando alguém entra na live"""
    user = event.user
    print(f"🎉 {user.nickname} entrou na live!")
    socketio.emit('join', {
        'nickname': user.nickname,
        'unique_id': user.unique_id,
        'avatar': user.avatar_thumb.urls[0] if user.avatar_thumb and user.avatar_thumb.urls else None
    })

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(f"💬 {event.user.nickname}: {event.comment}")
    socketio.emit('comment', {
        'nickname': event.user.nickname,
        'comment': event.comment,
        'avatar': event.user.avatar_thumb.urls[0] if event.user.avatar_thumb and event.user.avatar_thumb.urls else None
    })

@app.route('/')
def index():
    return render_template('index.html')

def run_tiktok_client():
    """Roda o cliente TikTok em uma thread separada"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(client.start())
    except Exception as e:
        print(f"Erro no cliente TikTok: {e}")

if __name__ == '__main__':
    # Inicia o cliente TikTok em uma thread separada
    tiktok_thread = threading.Thread(target=run_tiktok_client, daemon=True)
    tiktok_thread.start()
    
    # Pega a porta do ambiente (Render usa PORT)
    port = int(os.getenv("PORT", 5000))
    
    # Inicia o servidor Flask
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
