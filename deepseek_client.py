import httpx
from config import Config

class DeepSeekClient:
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError('? DEEPSEEK_API_KEY is required!')

    async def call_deepseek(self, message, history):
        messages = []
        
        # System prompt
        messages.append({
            'role': 'system',
            'content': 'Jestes pomocnym asystentem AI. Odpowiadaj zwiezle i na temat.'
        })
        
        # Historia
        recent_history = history[-10:] if len(history) > 10 else history
        messages.extend(recent_history)
        
        # Aktualna wiadomosc
        messages.append({
            'role': 'user',
            'content': message
        })
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://api.deepseek.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'deepseek-chat',
                        'messages': messages,
                        'temperature': 0.7,
                        'max_tokens': 2000
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                reply = data['choices'][0]['message']['content']
                
                return {
                    'reply': reply,
                    'model': data.get('model', 'deepseek-chat')
                }
                
        except Exception as e:
            return {'reply': f'? Blad DeepSeek: {str(e)}', 'error': True}

deepseek_client = DeepSeekClient()
