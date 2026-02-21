from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import time

from config import Config
from memory import AlfaBridgeMemory
from deepseek_client import deepseek_client

app = FastAPI(title='ALFA Bridge', version='1.0.0')
memory = AlfaBridgeMemory(Config.MEMORY_FILE)

class QueryRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    reply: str
    memory_snapshot: list
    meta: dict

def verify_token(x_alfa_token: Optional[str] = None):
    if Config.ALFA_SERVICE_TOKEN and x_alfa_token != Config.ALFA_SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail='? Invalid X-ALFA-TOKEN')

@app.get('/')
async def root():
    return {'status': '? ALFA Bridge active'}

@app.post('/bridge/query', response_model=QueryResponse)
async def bridge_query(request: QueryRequest, x_alfa_token: Optional[str] = Header(None)):
    verify_token(x_alfa_token)
    
    start_time = time.time()
    
    try:
        # Wczytaj historie
        history = memory.load_history(request.user_id, request.session_id)
        print(f'?? User: {request.user_id}, History: {len(history)} messages')
        
        # Wywolaj DeepSeek
        deepseek_response = await deepseek_client.call_deepseek(request.message, history)
        reply = deepseek_response['reply']
        
        # Zapisz do pamieci
        memory.append_entry(request.user_id, 'user', request.message, request.session_id)
        memory.append_entry(request.user_id, 'assistant', reply, request.session_id)
        
        # Pobierz zaktualizowana historie
        updated_history = memory.load_history(request.user_id, request.session_id)
        
        elapsed = time.time() - start_time
        
        print(f'? Response: {len(reply)} chars, time: {elapsed:.2f}s')
        
        return QueryResponse(
            reply=reply,
            memory_snapshot=updated_history[-3:],
            meta={
                'engine': 'deepseek',
                'user_id': request.user_id,
                'response_time_ms': int(elapsed * 1000),
                'history_length': len(updated_history)
            }
        )
        
    except Exception as e:
        print(f'? Error: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Bridge error: {str(e)}')

@app.get('/health')
async def health_check():
    return {
        'status': 'healthy',
        'deepseek_configured': bool(Config.DEEPSEEK_API_KEY)
    }

@app.on_event('startup')
async def startup_event():
    print('=' * 50)
    print('?? ALFA BRIDGE v1.0 - STARTED')
    print('=' * 50)
    print(f'?? Service token: {Config.ALFA_SERVICE_TOKEN}')
    print('?? Server ready!')
    print('=' * 50)
