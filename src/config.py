import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / '.env')

def env(name: str, default: str = '') -> str:
    return os.getenv(name, default)

OLLAMA_URL = env('OLLAMA_URL', 'http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL = env('OLLAMA_MODEL', 'qwen2.5:3b')
OLLAMA_TIMEOUT = int(env('OLLAMA_TIMEOUT', '120'))
DB = {
    'host': env('MYSQL_HOST', '127.0.0.1'),
    'port': int(env('MYSQL_PORT', '3306')),
    'database': env('MYSQL_DATABASE', 'locadora_ia_demo'),
    'user': env('MYSQL_USER', 'locadora_bot_read'),
    'password': env('MYSQL_PASSWORD'),
    'connection_timeout': 10,
}
