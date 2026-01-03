from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, JoinEvent, DisconnectEvent
import asyncio
import logging

# Ativa logs detalhados
logging.basicConfig(level=logging.DEBUG)

print("Iniciando teste de conexao...")
print("Username: aliviamor")

client = TikTokLiveClient('aliviamor')

@client.on(ConnectEvent)
async def on_connect(event):
    print('=' * 50)
    print('CONECTADO COM SUCESSO!')
    print(f'Room ID: {client.room_id}')
    print('=' * 50)

@client.on(DisconnectEvent)
async def on_disconnect(event):
    print('DESCONECTADO')

@client.on(JoinEvent)
async def on_join(event):
    print(f'Entrou: {event.user.unique_id}')

async def main():
    print("Tentando conectar...")
    try:
        await client.start()
        print("client.start() retornou")
    except Exception as e:
        print(f'ERRO: {type(e).__name__}')
        print(f'Mensagem: {e}')
        import traceback
        traceback.print_exc()

print("Rodando asyncio...")
asyncio.run(main())
print("Fim do script")
