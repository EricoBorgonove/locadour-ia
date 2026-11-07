import json
import requests
from .config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

class LLMError(RuntimeError):
    pass

def conversa(system: str, user: str, json_mode: bool = False) -> str:
    body = {
        'model': OLLAMA_MODEL,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        'stream': False,
        'options': {'temperature': 0},
    }
    if json_mode:
        body['format'] = 'json'
    try:
        response = requests.post(f'{OLLAMA_URL}/api/chat', json=body, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
        output = response.json()['message']['content'].strip()
        if not output:
            raise LLMError('Modelo retornou uma resposta vazia.')
        return output
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise LLMError(f'Falha ao consultar Ollama: {exc}') from exc

def objeto_json(texto: str) -> dict:
    try:
        obj = json.loads(texto)
        if not isinstance(obj, dict):
            raise ValueError('JSON não é objeto')
        return obj
    except ValueError as exc:
        raise LLMError('Agente retornou JSON inválido.') from exc
