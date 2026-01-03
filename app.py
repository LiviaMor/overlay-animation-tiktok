import asyncio
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from TikTokLive import TikTokLiveClient
from TikTokLive.events import JoinEvent, ConnectEvent, DisconnectEvent

import os

TIKTOK_USERNAME = os.environ.get("TIKTOK_USERNAME", "aliviamor")
FLASK_PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tiktok-overlay-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def home():
    return '<h1>TikTok Live Overlay</h1><p>Acesse <a href="/overlay">/overlay</a></p><p><a href="/test">Clique aqui para testar</a></p>'

@app.route('/test')
def test():
    """Rota de teste - simula um usuário entrando na live"""
    socketio.emit('new_viewer', {
        'unique_id': 'usuario_teste',
        'avatar_url': 'https://p16-sign-sg.tiktokcdn.com/aweme/100x100/tos-alisg-avt-0068/7b0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c.jpeg'
    })
    return 'Teste enviado! Verifique o overlay.'

@app.route('/overlay')
def overlay():
    response = app.make_response(render_template('index.html'))
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

client = TikTokLiveClient(unique_id=TIKTOK_USERNAME)

# Session ID para autenticação (pegar dos cookies do TikTok)
SESSION_ID = os.environ.get("TIKTOK_SESSION_ID", "")
if SESSION_ID:
    client.web.set_session_id(SESSION_ID)
    print(f"[TikTok] Usando session_id: {SESSION_ID[:10]}...")

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Conectado a live de @{TIKTOK_USERNAME}")

@client.on(DisconnectEvent)
async def on_disconnect(event: DisconnectEvent):
    print(f"Desconectado da live")

@client.on(JoinEvent)
async def on_join(event: JoinEvent):
    unique_id = event.user.unique_id
    avatar_url = ""
    
    # Tenta diferentes formas de pegar o avatar
    try:
        if hasattr(event.user, 'avatar_thumb') and event.user.avatar_thumb:
            thumb = event.user.avatar_thumb
            if hasattr(thumb, 'm_urls') and thumb.m_urls:
                avatar_url = thumb.m_urls[0]
            elif hasattr(thumb, 'url_list') and thumb.url_list:
                avatar_url = thumb.url_list[0]
            elif hasattr(thumb, 'urls') and thumb.urls:
                avatar_url = thumb.urls[0]
    except Exception as e:
        print(f"Erro ao pegar avatar: {e}")
        avatar_url = ""
    
    print(f"Novo espectador: @{unique_id} | Avatar: {avatar_url[:80] if avatar_url else 'sem avatar'}...")
    socketio.emit('new_viewer', {'unique_id': unique_id, 'avatar_url': avatar_url})

def run_tiktok_client():
    print("[TikTok] Iniciando cliente...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print(f"[TikTok] Conectando a live de @{TIKTOK_USERNAME}...")
        
        async def run():
            task = await client.start(process_connect_events=True)
            print("[TikTok] Conectado! Aguardando eventos...")
            await task
        
        loop.run_until_complete(run())
    except Exception as e:
        print(f"[TikTok] Erro ao conectar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import sys
    print("=" * 50, flush=True)
    print("TikTok Live Overlay", flush=True)
    print(f"Monitorando: @{TIKTOK_USERNAME}", flush=True)
    print(f"Porta: {FLASK_PORT}", flush=True)
    print("=" * 50, flush=True)
    sys.stdout.flush()
    
    print("Iniciando thread do TikTok...", flush=True)
    tiktok_thread = threading.Thread(target=run_tiktok_client, daemon=True)
    tiktok_thread.start()
    
    print("Iniciando servidor Flask...", flush=True)
    sys.stdout.flush()
    socketio.run(app, host='0.0.0.0', port=FLASK_PORT, debug=False)
