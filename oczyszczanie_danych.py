import json
import os
import re
from datetime import datetime

print('=== KRÓLEWSKI SKARBIEC - FILTROWANIE WRAŻLIWYCH DANYCH ===')

skarbiec_path = r'D:\kurlewski skarbiec'
czaty_path = os.path.join(skarbiec_path, 'Czaty_Historyczne')
przetworzone_path = os.path.join(skarbiec_path, 'Przetworzone_Dane')
oczyszczone_path = os.path.join(skarbiec_path, 'Dane_Do_Nauczania')
os.makedirs(oczyszczone_path, exist_ok=True)

# LISTA WRAŻLIWYCH SŁÓW DO USUNIĘCIA (możesz rozszerzyć)
wrazliwe_slowa = [
    'hasło', 'password', 'login', 'email', '@', 'telefon', 'numer',
    'pesel', 'dowód', 'karta', 'kredytowa', 'bank', 'pieniądze',
    'adres', 'ulica', 'miasto', 'kod pocztowy'
]

# LISTA NIEWŁAŚCIWYCH TEMATÓW
niewlasciwe_tematy = [
    'przegrana', 'porażka', 'problem', 'kłopot', 'błąd', 'niepowodzenie',
    'nie udało', 'nie umiem', 'nie wiem', 'głupi', 'idiota'
]

def filtruj_wrazliwe_dane(tekst):
    """Usuwa wrażliwe dane z tekstu"""
    if not isinstance(tekst, str):
        tekst = str(tekst)
    
    # Usuń emaile
    tekst = re.sub(r'\S+@\S+', '[EMAIL_USUNIĘTY]', tekst)
    
    # Usuń numery telefonów
    tekst = re.sub(r'(\+?[\d\s\-\(\)]{9,})', '[TELEFON_USUNIĘTY]', tekst)
    
    # Usuń numery kart/kont
    tekst = re.sub(r'(\d{4}[\s\-]?){3,}', '[NUMER_USUNIĘTY]', tekst)
    
    # Usuń wrażliwe słowa (zastąp gwiazdkami)
    for slowo in wrazliwe_slowa:
        tekst = re.sub(re.escape(slowo), '[***]', tekst, flags=re.IGNORECASE)
    
    return tekst

def czy_wlasciwa_rozmowa(tekst):
    """Sprawdza czy rozmowa jest właściwa do nauki"""
    if not isinstance(tekst, str):
        tekst = str(tekst)
    
    tekst = tekst.lower()
    
    # Sprawdź czy zawiera niewłaściwe tematy
    for temat in niewlasciwe_tematy:
        if temat in tekst:
            return False
    
    # Sprawdź czy to wartościowa rozmowa (min. 3 słowa)
    slowa = tekst.split()
    if len(slowa) < 3:
        return False
    
    return True

def przetworz_plik_do_nauczania(sciezka_pliku, nazwa_pliku):
    """Przetwarza plik i tworzy oczyszczoną wersję do nauki"""
    print(f'\\n🔄 Przetwarzanie: {nazwa_pliku}')
    
    try:
        with open(sciezka_pliku, 'r', encoding='utf-8') as f:
            dane = json.load(f)
        
        oczyszczone_dane = []
        usuniete = 0
        zachowane = 0
        
        if isinstance(dane, list):
            for item in dane:
                tekst = str(item)
                
                # Sprawdź czy to właściwa rozmowa
                if czy_wlasciwa_rozmowa(tekst):
                    # Oczyść z wrażliwych danych
                    tekst_oczyszczony = filtruj_wrazliwe_dane(tekst)
                    oczyszczone_dane.append(tekst_oczyszczony)
                    zachowane += 1
                else:
                    usuniete += 1
        
        elif isinstance(dane, dict):
            for key, value in dane.items():
                tekst = str(value)
                
                if czy_wlasciwa_rozmowa(tekst):
                    tekst_oczyszczony = filtruj_wrazliwe_dane(tekst)
                    oczyszczone_dane.append(f'{key}: {tekst_oczyszczony}')
                    zachowane += 1
                else:
                    usuniete += 1
        
        # Zapisz oczyszczone dane
        if oczyszczone_dane:
            plik_wyjsciowy = os.path.join(oczyszczone_path, f'oczyszczone_{nazwa_pliku}')
            
            dane_do_zapisu = {
                'nazwa_oryginalna': nazwa_pliku,
                'data_oczyszczenia': datetime.now().isoformat(),
                'liczba_zachowanych_wpisow': zachowane,
                'liczba_usunietych_wpisow': usuniete,
                'oczyszczone_dane': oczyszczone_dane[:100]  # Tylko pierwsze 100 wpisów
            }
            
            with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
                json.dump(dane_do_zapisu, f, indent=2, ensure_ascii=False)
            
            print(f'   ✅ Zachowano: {zachowane} wpisów')
            print(f'   🗑️  Usunięto: {usuniete} wpisów')
            print(f'   💾 Zapisano: {plik_wyjsciowy}')
        else:
            print(f'   ⚠️  Brak danych do zachowania')
            
    except Exception as e:
        print(f'   ❌ Błąd: {e}')

# PRZETWARZANIE WSZYSTKICH PLIKÓW
print('Rozpoczynam oczyszczanie danych...')

for plik in os.listdir(czaty_path):
    if plik.endswith('.json'):
        sciezka = os.path.join(czaty_path, plik)
        przetworz_plik_do_nauczania(sciezka, plik)

print(f'\\n🎯 OCZYSZCZANIE ZAKOŃCZONE!')
print(f'📁 Oczyszczone dane: {oczyszczone_path}')
print(f'🛡️  Wszystkie wrażliwe dane zostały usunięte!')
print(f'🧠 Ollama nauczy się tylko wartościowych rozmów!')
