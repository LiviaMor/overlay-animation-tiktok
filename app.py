import asyncio
import threading
import os
import sys
import traceback
from flask import Flask, render_template
from flask_socketio import SocketIO
from TikTokLive import TikTokLiveClient
from TikTokLive.events import JoinEvent, ConnectEvent, DisconnectEvent
from httpx import Proxy

# Configurações via variáveis de ambiente
TIKTOK_USERNAME = os.environ.get("TIKTOK_USERNAME", "aliviamor")
FLASK_PORT = int(os.environ.get("PORT", 10000))
SESSION_ID = os.environ.get("TIKTOK_SESSION_ID", "eaf98b4b3f3a60b2c1bcf3c6489346df")
PROXY_URL = os.environ.get("PROXY_URL", "http://dvrpjsqr-rotate:w9z0s5imgeba@p.webshare.io:80/")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "tiktok-overlay-secret-key")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def home():
    return f'<h1>TikTok Live Overlay</h1><p>Monitorando: <b>@{TIKTOK_USERNAME}</b></p><p>Acesse <a href="/overlay">/overlay</a></p><p><a href="/test">Clique aqui para testar</a></p>'

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
    # Útil se estiver usando ngrok para testes locais
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

# Configuração do Cliente TikTok
client_kwargs = {}

def format_proxy_url(proxy_str):
    """
    Converte formatos comuns de proxy para o formato de URL exigido pelo httpx.
    Ex: 142.111.48.253:7030:user:pass -> http://user:pass@142.111.48.253:7030
    """
    if not proxy_str:
        return None
    
    # Se já estiver no formato correto, retorna
    if proxy_str.startswith(('http://', 'https://', 'socks5://')):
        return proxy_str
    
    # Tenta lidar com o formato IP:PORTA:USER:PASS
    parts = proxy_str.split(':')
    if len(parts) == 4:
        ip, port, user, password = parts
        return f"http://{user}:{password}@{ip}:{port}"
    
    # Tenta lidar com o formato IP:PORTA
    if len(parts) == 2:
        return f"http://{proxy_str}"
        
    return proxy_str

if PROXY_URL:
    formatted_proxy = format_proxy_url(PROXY_URL)
    print(f"[TikTok] Proxy original: {PROXY_URL}")
    print(f"[TikTok] Proxy formatado: {formatted_proxy.split('@')[-1] if '@' in formatted_proxy else formatted_proxy}")
    try:
        # Na versão 6.x+, o parâmetro correto é 'web_proxy'
        client_kwargs['web_proxy'] = Proxy(url=formatted_proxy)
    except Exception as e:
        print(f"[TikTok] Erro ao configurar proxy: {e}")

client = TikTokLiveClient(unique_id=TIKTOK_USERNAME, **client_kwargs)

if SESSION_ID:
    # Na versão 6.x+, o método correto é 'set_session'
    client.web.set_session(SESSION_ID)
    print(f"[TikTok] Usando session_id: {SESSION_ID[:10]}...")

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"[TikTok] CONECTADO com sucesso à live de @{TIKTOK_USERNAME}")

@client.on(DisconnectEvent)
async def on_disconnect(event: DisconnectEvent):
    print(f"[TikTok] DESCONECTADO da live. Tentando reconectar em 10 segundos...")
    await asyncio.sleep(10)
    # A biblioteca TikTokLive geralmente tenta reconectar sozinha se configurada, 
    # mas logs ajudam a debugar.

@client.on(JoinEvent)
async def on_join(event: JoinEvent):
    unique_id = event.user.unique_id
    avatar_url = ""
    
    try:
        # Tenta pegar a melhor qualidade de avatar disponível
        if hasattr(event.user, 'avatar_thumb') and event.user.avatar_thumb:
            thumb = event.user.avatar_thumb
            for attr in ['m_urls', 'url_list', 'urls']:
                if hasattr(thumb, attr) and getattr(thumb, attr):
                    avatar_url = getattr(thumb, attr)[0]
                    break
    except Exception as e:
        print(f"[TikTok] Erro ao processar avatar de @{unique_id}: {e}")
    
    print(f"[TikTok] Novo espectador: @{unique_id}")
    socketio.emit('new_viewer', {'unique_id': unique_id, 'avatar_url': avatar_url})

def run_tiktok_client():
    print("[TikTok] Iniciando thread do cliente...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def connect_with_retry():
        while True:
            try:
                print(f"[TikTok] Tentando conectar a @{TIKTOK_USERNAME}...")
                await client.start()
            except Exception as e:
                print(f"[TikTok] Erro crítico na conexão: {e}")
                traceback.print_exc()
                print("[TikTok] Reiniciando em 15 segundos...")
                await asyncio.sleep(15)

    loop.run_until_complete(connect_with_retry())

if __name__ == '__main__':
    print("=" * 50)
    print("TIKTOK LIVE OVERLAY - INICIANDO")
    print(f"Monitorando: @{TIKTOK_USERNAME}")
    print(f"Porta: {FLASK_PORT}")
    print("=" * 50)
    sys.stdout.flush()
    
    # Inicia o cliente TikTok em uma thread separada
    tiktok_thread = threading.Thread(target=run_tiktok_client, daemon=True)
    tiktok_thread.start()
    
    # Inicia o servidor Flask com SocketIO
    print("[Flask] Iniciando servidor...")
    socketio.run(app, host='0.0.0.0', port=FLASK_PORT, debug=False)
