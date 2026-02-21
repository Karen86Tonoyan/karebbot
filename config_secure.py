import os
from dotenv import load_dotenv
load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
ALFA_SERVICE_TOKEN = os.getenv('ALFA_SERVICE_TOKEN', 'alfa_secret_token_629173')

if not DEEPSEEK_API_KEY:
    raise ValueError('DEEPSEEK_API_KEY not set!')
