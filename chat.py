from fastapi import APIRouter

chat_router = APIRouter(prefix=\"/ai\", tags=[\"ai\"])

@chat_router.get(\"/deepseek\")
def deepseek_chat():
    return {\"message\": \"DeepSeek AI endpoint ready! ??\"}
