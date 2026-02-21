from fastapi import FastAPI
from auth.router import auth_router
from ai.chat import chat_router

app = FastAPI(title=\"Alfa Bridge\")
app.include_router(auth_router)
app.include_router(chat_router)

@app.get(\"/\")
def read_root():
    return {\"message\": \"?? Alfa Bridge API - Veritas Supra Omnia\"}
