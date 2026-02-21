from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    user_id: str
    message: str

@app.post('/bridge/query')
def bridge_query(query: Query):
    return {
        'reply': f'DZIALA! Otrzymalem: {query.message}',
        'memory_snapshot': [{'test': 'data'}],
        'meta': {'status': 'success'}
    }

@app.get('/')
def root():
    return {'status': 'ALFA Bridge WORKS!'}

print('=== SERVER READY ===')
