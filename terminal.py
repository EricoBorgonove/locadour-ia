import logging
from src.agentes import SistemaTresAgentes
from src.config import env

logging.basicConfig(level=env('LOG_LEVEL','INFO'))
app = SistemaTresAgentes()
print('Locadora IA: 3 agentes | digite sair para encerrar')
while True:
    try:
        texto = input('\nVocê: ').strip()
    except (EOFError, KeyboardInterrupt):
        print('\nEncerrado.')
        break
    if texto.lower() in {'sair','exit','quit'}:
        break
    print('\nLocadora:', app.responder(texto))
