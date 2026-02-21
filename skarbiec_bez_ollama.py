import os
import json
from datetime import datetime

print('=== KRÓLEWSKI SKARBIEC - SYSTEM BEZ OLLAMA ===')

skarbiec_path = r'D:\kurlewski skarbiec'
czaty_path = os.path.join(skarbiec_path, 'Czaty_Historyczne')

if not os.path.exists(czaty_path):
    print('ERROR - Nie znaleziono Skarbca')
    exit()

print('✅ Skarbiec znaleziony')

# STWÓRZ FOLDER DLA PRZETWORZONYCH DANYCH
przetworzone_path = os.path.join(skarbiec_path, 'Przetworzone_Dane')
os.makedirs(przetworzone_path, exist_ok=True)

print('🔄 Przetwarzanie plików...')

for plik in os.listdir(czaty_path):
    if plik.endswith('.json'):
        sciezka = os.path.join(czaty_path, plik)
        rozmiar_mb = os.path.getsize(sciezka) // 1024 // 1024
        
        print(f'\\n📁 {plik} ({rozmiar_mb}MB)')
        
        try:
            # PRZECZYTAJ I ZAPISZ STRESZCZENIE
            with open(sciezka, 'r', encoding='utf-8') as f:
                dane = json.load(f)
            
            # STWÓRZ STRESZCZENIE
            if isinstance(dane, list):
                liczba_wpisow = len(dane)
                pierwszy_wpis = str(dane[0])[:100] if dane else 'Brak'
                ostatni_wpis = str(dane[-1])[:100] if dane else 'Brak'
            elif isinstance(dane, dict):
                liczba_wpisow = len(dane.keys())
                klucze = list(dane.keys())[:5]
                pierwszy_wpis = f'Klucze: {klucze}'
                ostatni_wpis = 'Słownik'
            else:
                liczba_wpisow = 1
                pierwszy_wpis = str(dane)[:100]
                ostatni_wpis = str(dane)[-100:] if len(str(dane)) > 100 else ''
            
            # ZAPISZ STRESZCZENIE
            streszczenie = {
                'nazwa_pliku': plik,
                'data_przetworzenia': datetime.now().isoformat(),
                'rozmiar_oryginalny_mb': rozmiar_mb,
                'liczba_wpisow': liczba_wpisow,
                'przykladowe_dane': {
                    'pierwszy_wpis': pierwszy_wpis,
                    'ostatni_wpis': ostatni_wpis
                },
                'status': 'przetworzony'
            }
            
            # ZAPISZ DO NOWEGO PLIKU
            nazwa_streszczenia = f'streszczenie_{os.path.splitext(plik)[0]}.json'
            sciezka_streszczenia = os.path.join(przetworzone_path, nazwa_streszczenia)
            
            with open(sciezka_streszczenia, 'w', encoding='utf-8') as f:
                json.dump(streszczenie, f, indent=2, ensure_ascii=False)
            
            print(f'   ✅ Streszczenie zapisane: {nazwa_streszczenia}')
            print(f'   📊 Wpisy: {liczba_wpisow}')
            
        except Exception as e:
            print(f'   ❌ Błąd: {e}')

print(f'\\n🎯 SYSTEM UKOŃCZONY!')
print(f'📁 Przetworzone pliki: {przetworzone_path}')
print(f'💾 Możesz później użyć tych danych z Ollama gdy będzie szybsza')
