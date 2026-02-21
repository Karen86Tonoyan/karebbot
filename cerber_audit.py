import os
import re

PATTERNS = [
    r'api[_-]?key[\"\s:=]+[a-zA-Z0-9]{20,}',
    r'token[\"\s:=]+[a-zA-Z0-9]{20,}',
    r'password[\"\s:=]+[^\s]{8,}',
    r'Bearer [a-zA-Z0-9\-._~+/]+=*',
]

print("🐺 CERBER Python Audit")
print("="*50)

leaks = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules']]
    
    for file in files:
        if file.endswith(('.php', '.js', '.html', '.py', '.env')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE):
                            print(f"🔴 {path}: {pattern}")
                            leaks += 1
                            break
            except:
                pass

print("="*50)
print(f"Leaks found: {leaks}")
if leaks == 0:
    print("✅ CERBER APPROVED")
else:
    print("❌ FIX IMMEDIATELY")
