#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                         ALFA - AI FEDERATION APP
═══════════════════════════════════════════════════════════════════════════════

Legalna aplikacja typu Gemini z możliwością podłączenia wielu AI.
Logowanie przez Google OAuth - wszystkie AI używają Twoich oficjalnych kont.

Obsługiwane AI:
- Google Gemini (przez Google Cloud)
- OpenAI GPT-4 / GPT-4o
- Anthropic Claude
- DeepSeek
- Ollama (lokalne modele)

Autor: Karen86Tonoyan
Licencja: Apache 2.0
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# FastAPI
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import local modules
sys.path.insert(0, str(Path(__file__).parent / "ollama-plugins"))
from google_auth import get_auth_manager, GoogleAuthManager
from ai_models import get_model_manager, AIModelManager


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

APP_NAME = "ALFA - AI Federation"
VERSION = "1.0.0"
HOST = "127.0.0.1"
PORT = 8765

# Supported AI providers (legal, official APIs)
AI_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "description": "Google's multimodal AI",
        "models": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"],
        "auth_type": "google_oauth",  # Uses Google login!
        "official_url": "https://ai.google.dev/"
    },
    "openai": {
        "name": "OpenAI GPT",
        "description": "ChatGPT / GPT-4",
        "models": ["gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "auth_type": "api_key",
        "official_url": "https://platform.openai.com/"
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "description": "Claude AI",
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        "auth_type": "api_key",
        "official_url": "https://console.anthropic.com/"
    },
    "deepseek": {
        "name": "DeepSeek",
        "description": "DeepSeek Coder & Chat",
        "models": ["deepseek-chat", "deepseek-coder"],
        "auth_type": "api_key",
        "official_url": "https://platform.deepseek.com/"
    },
    "ollama": {
        "name": "Ollama (Local)",
        "description": "Local AI models - 100% private",
        "models": ["llama3", "mistral", "codellama", "deepseek-r1"],
        "auth_type": "none",
        "official_url": "https://ollama.ai/"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    model: Optional[str] = None
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    model: str = "gemini-pro"
    conversation_id: Optional[str] = None


class APIKeyConfig(BaseModel):
    provider: str
    api_key: str


class UserSession:
    """User session with API keys and conversation history"""
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.api_keys: Dict[str, str] = {}
        self.conversations: Dict[str, List[ChatMessage]] = {}
        self.created_at = datetime.now()
        self.config_path = Path.home() / ".alfa" / "users" / f"{user_email}.json"
        self._load()
    
    def _load(self):
        """Load user config from disk"""
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text())
                self.api_keys = data.get("api_keys", {})
            except Exception:
                pass
    
    def _save(self):
        """Save user config to disk (encrypted in production)"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "user_email": self.user_email,
            "api_keys": self.api_keys,  # TODO: Encrypt with CERBER
            "updated_at": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2))
    
    def set_api_key(self, provider: str, key: str):
        """Set API key for provider"""
        self.api_keys[provider] = key
        self._save()
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider"""
        return self.api_keys.get(provider)


# ═══════════════════════════════════════════════════════════════════════════════
# AI FEDERATION - Multi-Model Chat
# ═══════════════════════════════════════════════════════════════════════════════

class AIFederation:
    """
    Federacja AI - łączy wiele modeli AI w jeden interfejs.
    Każdy model używa LEGALNYCH, OFICJALNYCH API.
    """
    
    def __init__(self):
        self.model_manager = get_model_manager()
        self.sessions: Dict[str, UserSession] = {}
    
    def get_session(self, user_email: str) -> UserSession:
        """Get or create user session"""
        if user_email not in self.sessions:
            self.sessions[user_email] = UserSession(user_email)
        return self.sessions[user_email]
    
    async def chat(
        self, 
        user_email: str,
        message: str, 
        model: str = "gemini-pro",
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message to AI model.
        Uses user's own API keys (legal!).
        """
        session = self.get_session(user_email)
        
        # Determine provider from model name
        provider = self._get_provider(model)
        
        # Check if we have API key (except Ollama which is local)
        if provider != "ollama":
            api_key = session.get_api_key(provider)
            if not api_key:
                return {
                    "error": f"API key not configured for {provider}",
                    "setup_url": AI_PROVIDERS[provider]["official_url"],
                    "message": f"Please add your {AI_PROVIDERS[provider]['name']} API key in Settings"
                }
        
        try:
            # Call the appropriate AI
            response = await self._call_ai(provider, model, message, session)
            
            return {
                "success": True,
                "model": model,
                "provider": provider,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "model": model,
                "provider": provider
            }
    
    def _get_provider(self, model: str) -> str:
        """Get provider name from model name"""
        model_lower = model.lower()
        
        if "gemini" in model_lower:
            return "gemini"
        elif "gpt" in model_lower:
            return "openai"
        elif "claude" in model_lower:
            return "anthropic"
        elif "deepseek" in model_lower and "ollama" not in model_lower:
            return "deepseek"
        else:
            return "ollama"  # Default to local
    
    async def _call_ai(
        self, 
        provider: str, 
        model: str, 
        message: str,
        session: UserSession
    ) -> str:
        """Call specific AI provider"""
        
        if provider == "gemini":
            return await self._call_gemini(model, message, session)
        elif provider == "openai":
            return await self._call_openai(model, message, session)
        elif provider == "anthropic":
            return await self._call_claude(model, message, session)
        elif provider == "deepseek":
            return await self._call_deepseek(model, message, session)
        else:
            return await self._call_ollama(model, message)
    
    async def _call_gemini(self, model: str, message: str, session: UserSession) -> str:
        """Call Google Gemini API"""
        import google.generativeai as genai
        
        api_key = session.get_api_key("gemini")
        genai.configure(api_key=api_key)
        
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(message)
        
        return response.text
    
    async def _call_openai(self, model: str, message: str, session: UserSession) -> str:
        """Call OpenAI API"""
        from openai import OpenAI
        
        client = OpenAI(api_key=session.get_api_key("openai"))
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}]
        )
        
        return response.choices[0].message.content
    
    async def _call_claude(self, model: str, message: str, session: UserSession) -> str:
        """Call Anthropic Claude API"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=session.get_api_key("anthropic"))
        
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": message}]
        )
        
        return response.content[0].text
    
    async def _call_deepseek(self, model: str, message: str, session: UserSession) -> str:
        """Call DeepSeek API"""
        import httpx
        
        api_key = session.get_api_key("deepseek")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message}]
                }
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_ollama(self, model: str, message: str) -> str:
        """Call local Ollama"""
        import httpx
        
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{ollama_host}/api/generate",
                json={
                    "model": model.replace("ollama-", ""),
                    "prompt": message,
                    "stream": False
                }
            )
            data = response.json()
            return data.get("response", "No response from Ollama")


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Multi-AI Federation with Google OAuth"
)

# CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
auth_manager = get_auth_manager()
ai_federation = AIFederation()


# ─────────────────────────────────────────────────────────────────────────────
# AUTH ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def home():
    """Home page"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALFA - AI Federation</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                min-height: 100vh;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                padding: 40px;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle {
                color: #a0a0a0;
                margin-bottom: 40px;
            }
            .login-btn {
                background: #4285f4;
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 18px;
                border-radius: 8px;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                text-decoration: none;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .login-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(66, 133, 244, 0.4);
            }
            .features {
                display: flex;
                gap: 30px;
                margin-top: 60px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .feature {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 12px;
                width: 150px;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ALFA</h1>
            <p class="subtitle">AI Federation - Wszystkie AI w jednym miejscu</p>
            
            <a href="/auth/google" class="login-btn">
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path fill="white" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="white" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="white" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="white" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Zaloguj przez Google
            </a>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🌐</div>
                    <div>Gemini</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🤖</div>
                    <div>GPT-4</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🧠</div>
                    <div>Claude</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🚀</div>
                    <div>DeepSeek</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🏠</div>
                    <div>Ollama</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


@app.get("/auth/google")
async def google_login():
    """Redirect to Google OAuth"""
    auth_url = auth_manager.get_authorization_url()
    if auth_url.startswith("Error"):
        return JSONResponse({"error": auth_url}, status_code=500)
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
async def google_callback(code: str, state: str):
    """Handle Google OAuth callback"""
    result = auth_manager.exchange_code(code, state)
    
    if "error" in result:
        return JSONResponse(result, status_code=400)
    
    # Redirect to chat with session
    session_id = result["session_id"]
    return RedirectResponse(f"/chat?session={session_id}")


# ─────────────────────────────────────────────────────────────────────────────
# CHAT ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/chat")
async def chat_page(session: str):
    """Chat interface"""
    if not auth_manager.verify_session(session):
        return RedirectResponse("/")
    
    user = auth_manager.get_session(session)
    user_email = user["user"].get("email", "Unknown")
    user_name = user["user"].get("name", "User")
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALFA Chat</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #1a1a2e;
                color: white;
                margin: 0;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            .header {{
                background: #16213e;
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #2a2a4a;
            }}
            .logo {{ font-size: 1.5em; font-weight: bold; }}
            .user-info {{ display: flex; align-items: center; gap: 10px; }}
            .model-select {{
                background: #2a2a4a;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                cursor: pointer;
            }}
            .chat-container {{
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }}
            .message {{
                max-width: 80%;
                margin-bottom: 15px;
                padding: 12px 16px;
                border-radius: 12px;
                line-height: 1.5;
            }}
            .user-message {{
                background: #4285f4;
                margin-left: auto;
            }}
            .ai-message {{
                background: #2a2a4a;
            }}
            .input-container {{
                padding: 20px;
                background: #16213e;
                display: flex;
                gap: 10px;
            }}
            .input-container input {{
                flex: 1;
                padding: 15px;
                border-radius: 8px;
                border: none;
                background: #2a2a4a;
                color: white;
                font-size: 16px;
            }}
            .input-container button {{
                padding: 15px 30px;
                background: #4285f4;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }}
            .input-container button:hover {{
                background: #5294ff;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🤖 ALFA</div>
            <div class="user-info">
                <select class="model-select" id="model">
                    <optgroup label="Google">
                        <option value="gemini-pro">Gemini Pro</option>
                        <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    </optgroup>
                    <optgroup label="OpenAI">
                        <option value="gpt-4">GPT-4</option>
                        <option value="gpt-4o">GPT-4o</option>
                    </optgroup>
                    <optgroup label="Anthropic">
                        <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                        <option value="claude-3-opus">Claude 3 Opus</option>
                    </optgroup>
                    <optgroup label="DeepSeek">
                        <option value="deepseek-chat">DeepSeek Chat</option>
                    </optgroup>
                    <optgroup label="Local (Ollama)">
                        <option value="ollama-llama3">LLaMA 3</option>
                        <option value="ollama-mistral">Mistral</option>
                    </optgroup>
                </select>
                <span>👤 {user_name}</span>
                <a href="/settings?session={session}" style="color: #a0a0a0; text-decoration: none;">⚙️</a>
            </div>
        </div>
        
        <div class="chat-container" id="chat">
            <div class="message ai-message">
                Cześć {user_name}! 👋 Jestem ALFA - Twój asystent AI. 
                Wybierz model z listy i zacznij rozmowę!
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="message" placeholder="Napisz wiadomość..." autofocus>
            <button onclick="sendMessage()">Wyślij</button>
        </div>
        
        <script>
            const sessionId = "{session}";
            const chatContainer = document.getElementById('chat');
            const messageInput = document.getElementById('message');
            const modelSelect = document.getElementById('model');
            
            messageInput.addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') sendMessage();
            }});
            
            async function sendMessage() {{
                const message = messageInput.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage(message, 'user');
                messageInput.value = '';
                
                // Show typing indicator
                const typingId = 'typing-' + Date.now();
                chatContainer.innerHTML += `<div class="message ai-message" id="${{typingId}}">⏳ Myślę...</div>`;
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                try {{
                    const response = await fetch('/api/chat', {{
                        method: 'POST',
                        headers: {{ 
                            'Content-Type': 'application/json',
                            'X-Session-ID': sessionId
                        }},
                        body: JSON.stringify({{
                            message: message,
                            model: modelSelect.value
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    // Remove typing indicator
                    document.getElementById(typingId)?.remove();
                    
                    if (data.error) {{
                        addMessage('❌ ' + data.error + (data.setup_url ? '\\n\\n🔗 ' + data.setup_url : ''), 'ai');
                    }} else {{
                        addMessage(data.response, 'ai');
                    }}
                }} catch (e) {{
                    document.getElementById(typingId)?.remove();
                    addMessage('❌ Błąd połączenia: ' + e.message, 'ai');
                }}
            }}
            
            function addMessage(text, type) {{
                const div = document.createElement('div');
                div.className = 'message ' + (type === 'user' ? 'user-message' : 'ai-message');
                div.textContent = text;
                chatContainer.appendChild(div);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """)


@app.post("/api/chat")
async def api_chat(request: ChatRequest, req: Request):
    """API endpoint for chat"""
    session_id = req.headers.get("X-Session-ID")
    
    if not session_id or not auth_manager.verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = auth_manager.get_session(session_id)
    user_email = user["user"].get("email")
    
    result = await ai_federation.chat(
        user_email=user_email,
        message=request.message,
        model=request.model
    )
    
    return result


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/settings")
async def settings_page(session: str):
    """Settings page for API keys"""
    if not auth_manager.verify_session(session):
        return RedirectResponse("/")
    
    user = auth_manager.get_session(session)
    user_email = user["user"].get("email", "Unknown")
    
    # Get user's current API keys (masked)
    user_session = ai_federation.get_session(user_email)
    
    providers_html = ""
    for provider_id, provider in AI_PROVIDERS.items():
        if provider["auth_type"] == "api_key":
            has_key = "✅" if user_session.get_api_key(provider_id) else "❌"
            providers_html += f"""
            <div class="provider">
                <div class="provider-header">
                    <span>{has_key} {provider['name']}</span>
                    <a href="{provider['official_url']}" target="_blank" style="color: #4285f4;">Pobierz klucz →</a>
                </div>
                <input type="password" 
                       id="{provider_id}_key" 
                       placeholder="Wklej swój klucz API..."
                       class="api-input">
                <button onclick="saveKey('{provider_id}')" class="save-btn">Zapisz</button>
            </div>
            """
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALFA - Ustawienia</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                background: #1a1a2e;
                color: white;
                padding: 40px;
                max-width: 600px;
                margin: 0 auto;
            }}
            h1 {{ color: #4285f4; }}
            .provider {{
                background: #2a2a4a;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 15px;
            }}
            .provider-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }}
            .api-input {{
                width: 100%;
                padding: 12px;
                border-radius: 6px;
                border: none;
                background: #16213e;
                color: white;
                margin-bottom: 10px;
            }}
            .save-btn {{
                background: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
            }}
            .back-link {{
                color: #a0a0a0;
                text-decoration: none;
            }}
            .info {{
                background: #16213e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #4285f4;
            }}
        </style>
    </head>
    <body>
        <a href="/chat?session={session}" class="back-link">← Powrót do czatu</a>
        <h1>⚙️ Ustawienia API</h1>
        
        <div class="info">
            <strong>🔐 Twoje klucze są bezpiecznie przechowywane lokalnie.</strong><br>
            Każdy serwis AI wymaga własnego klucza API. Pobierz je z oficjalnych stron.
        </div>
        
        {providers_html}
        
        <script>
            const sessionId = "{session}";
            
            async function saveKey(provider) {{
                const key = document.getElementById(provider + '_key').value;
                if (!key) return alert('Wpisz klucz API');
                
                const response = await fetch('/api/settings/key', {{
                    method: 'POST',
                    headers: {{ 
                        'Content-Type': 'application/json',
                        'X-Session-ID': sessionId
                    }},
                    body: JSON.stringify({{ provider, api_key: key }})
                }});
                
                if (response.ok) {{
                    alert('✅ Klucz zapisany!');
                    location.reload();
                }} else {{
                    alert('❌ Błąd zapisu');
                }}
            }}
        </script>
    </body>
    </html>
    """)


@app.post("/api/settings/key")
async def save_api_key(config: APIKeyConfig, req: Request):
    """Save API key for provider"""
    session_id = req.headers.get("X-Session-ID")
    
    if not session_id or not auth_manager.verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = auth_manager.get_session(session_id)
    user_email = user["user"].get("email")
    
    session = ai_federation.get_session(user_email)
    session.set_api_key(config.provider, config.api_key)
    
    return {"success": True}


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": VERSION,
        "providers": list(AI_PROVIDERS.keys())
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    🤖 ALFA - AI Federation                    ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Multi-AI Chat z logowaniem przez Google                      ║
    ║                                                               ║
    ║  Obsługiwane AI:                                              ║
    ║  • Google Gemini                                              ║
    ║  • OpenAI GPT-4                                               ║
    ║  • Anthropic Claude                                           ║
    ║  • DeepSeek                                                   ║
    ║  • Ollama (lokalne)                                           ║
    ║                                                               ║
    ║  🌐 http://{HOST}:{PORT}                                       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host=HOST, port=PORT)
