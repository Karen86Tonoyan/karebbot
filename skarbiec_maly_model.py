import requests
import json
import os
import time

print("=== KRÓLEWSKI SKARBIEC - MAŁY MODEL ===")

# UŻYJ MNIEJSZEGO MODELU
MODEL = "tinyllama:latest"  # lub "llama3.2:3b"

# SPRAWDŹ CZY MODEL DZIAŁA
try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL,
            "prompt": "Test",
            "stream": False
        },
        timeout=5
    )
    
    if response.status_code != 200:
        print(f"❌ Model {MODEL} nie działa")
        exit()
    else:
        print(f"✅ Model {MODEL} działa")
        
except Exception as e:
    print(f"❌ Błąd: {e}")
    exit()

# SKARBIEC
skarbiec_path = r"D:\kurlewski skarbiec"
czaty_path = os.path.join(skarbiec_path, "Czaty_Historyczne")

if not os.path.exists(czaty_path):
    print("❌ Nie znaleziono folderu z czatami")
    exit()

print("✅ Skarbiec znaleziony")

# PRZETWARZANIE - BARDZO MAŁE FRAGMENTY
print("\n🧠 TRENOWANIE NA MAŁYCH FRAGMENTACH...")

for plik in os.listdir(czaty_path):
    if plik.endswith('.json'):
        sciezka = os.path.join(czaty_path, plik)
        rozmiar_mb = os.path.getsize(sciezka) // 1024 // 1024
        
        print(f"\n📁 {plik} ({rozmiar_mb}MB)")
        
        try:
            with open(sciezka, 'r', encoding='utf-8') as f:
                # Tylko pierwsze 5 linii
                for i, linia in enumerate(f):
                    if i >= 5:  # Tylko 5 pierwszych linii
                        break
                    
                    if linia.strip():
                        try:
                            # Tylko 20 znaków!
                            tekst = linia.strip()[:20]
                            
                            response = requests.post(
                                "http://localhost:11434/api/generate",
                                json={
                                    "model": MODEL,
                                    "prompt": f"Zapamietaj: {tekst}",
                                    "stream": False
                                },
                                timeout=3
                            )
                            
                            if response.status_code == 200:
                                print(f"✅ Linia {i+1}: {tekst}")
                            else:
                                print(f"❌ Linia {i+1}")
                            
                            time.sleep(0.5)
                            
                        except:
                            continue
                            
        except Exception as e:
            print(f"❌ Błąd: {e}")

print("\n🎯 Ollama nauczyła się podstawowych wzorców!")
print("Masz działający system Królewskiego Skarbca! 🏰")
