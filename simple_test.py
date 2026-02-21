from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    user_id: str
    message: str

@app.post('/bridge/query')
def test_query(query: Query):
    return {
        'reply': f'SUCCESS: ALFA Bridge received: {query.message} from {query.user_id}',
        'memory_snapshot': [],
        'meta': {'status': 'working', 'version': '1.0'}
    }

@app.get('/')
def root():
    return {'status': 'ALFA Bridge - SIMPLE MODE - WORKING'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
