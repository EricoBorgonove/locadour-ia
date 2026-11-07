"""Integração Neonize. Execução de mensagens em sequência protegida por lock."""
import logging
import threading
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize import extract_text
from src.agentes import SistemaTresAgentes
from src.config import env

logging.basicConfig(level=env('LOG_LEVEL','INFO'))
client = NewClient(env('WHATSAPP_SESSION','session_locadora.db'))
app = SistemaTresAgentes()
lock = threading.Lock()

@client.event(ConnectedEv)
def conectado(client: NewClient, event: ConnectedEv):
    logging.info('WhatsApp conectado. Bot pronto.')

@client.event(MessageEv)
def mensagem(client: NewClient, event: MessageEv):
    try:
        source = event.Info.MessageSource
        if getattr(source, 'IsFromMe', False):
            return
        jid = source.Chat
        if '@g.us' in str(jid) and env('ALLOW_GROUPS', 'false').lower() != 'true':
            return
        texto = (extract_text(event.Message) or '').strip()
        if not texto or len(texto) > 1000:
            return
        logging.info('Nova mensagem recebida (tamanho=%s)', len(texto))
        # O cliente Neonize pode invocar handlers concorrentes; limita consultas simultâneas.
        with lock:
            admin_ids = {x.strip() for x in env('ADMIN_JIDS', '').split(',') if x.strip()}
            remetente = str(source.Sender)
            resposta = app.responder(texto, administrativo=(remetente in admin_ids))
            client.reply_message(resposta, event)
    except Exception:
        logging.exception('Falha ao processar mensagem do WhatsApp')

if __name__ == '__main__':
    client.connect()
