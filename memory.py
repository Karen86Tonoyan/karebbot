import json
import os
from pathlib import Path
import threading

class AlfaBridgeMemory:
    def __init__(self, file_path='bridge_memory.json'):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        if not self.file_path.exists():
            self._save_data({})

    def _load_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def _save_data(self, data):
        with self._lock:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load_history(self, user_id, session_id=None):
        data = self._load_data()
        session_key = session_id or 'default'
        user_data = data.get(user_id, {})
        return user_data.get(session_key, [])

    def append_entry(self, user_id, role, content, session_id=None, max_length=20):
        data = self._load_data()
        session_key = session_id or 'default'
        
        if user_id not in data:
            data[user_id] = {}
        if session_key not in data[user_id]:
            data[user_id][session_key] = []
        
        data[user_id][session_key].append({'role': role, 'content': content})
        
        if len(data[user_id][session_key]) > max_length:
            data[user_id][session_key] = data[user_id][session_key][-max_length:]
        
        self._save_data(data)
