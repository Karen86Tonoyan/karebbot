import json
import os
import re
from datetime import datetime

print('=== BEZPIECZNE OCZYSZCZANIE - BRAK RAPORTÓW Z DANYMI WRAŻLIWYMI ===')

skarbiec_path = r'D:\kurlewski skarbiec'
czaty_path = os.path.join(skarbiec_path, 'Czaty_Historyczne')
oczyszczone_path = os.path.join(skarbiec_path, 'Dane_Do_Nauczania')
os.makedirs(oczyszczone_path, exist_ok=True)

def bezpieczne_oczyszczanie(sciezka_pliku, nazwa_pliku):
    print(f'\\n🔄 Bezpieczne przetwarzanie: {nazwa_pliku}')
    
    try:
        with open(sciezka_pliku, 'r', encoding='utf-8') as f:
            dane = json.load(f)
        
        oczyszczone_dane = []
        liczba_oczyszczonych = 0
        
        if isinstance(dane, list):
            for item in dane:
                tekst = str(item)
                tekst_bezpieczny = usun_wrazliwe_dane(tekst)
                
                if czy_wartosciowa_rozmowa(tekst_bezpieczny):
                    oczyszczone_dane.append(tekst_bezpieczny)
                    liczba_oczyszczonych += 1
        
        elif isinstance(dane, dict):
            for key, value in dane.items():
                tekst = str(value)
                tekst_bezpieczny = usun_wrazliwe_dane(tekst)
                
                if czy_wartosciowa_rozmowa(tekst_bezpieczny):
                    oczyszczone_dane.append(f'{key}: {tekst_bezpieczny}')
                    liczba_oczyszczonych += 1
        
        # ZAPISZ TYLKO BEZPIECZNE DANE
        if oczyszczone_dane:
            plik_wyjsciowy = os.path.join(oczyszczone_path, f'bezpieczne_{nazwa_pliku}')
            
            dane_do_zapisu = {
                'nazwa_oryginalna': nazwa_pliku,
                'data_oczyszczenia': datetime.now().isoformat(),
                'liczba_bezpiecznych_wpisow': liczba_oczyszczonych,
                'uwaga': 'Wszystkie wrażliwe dane zostały TRWALE USUNIĘTE',
                'bezpieczne_dane': oczyszczone_dane[:50]  # Tylko bezpieczne dane
            }
            
            with open(plik_wyjsciowy, 'w', encoding='utf-8') as f:
                json.dump(dane_do_zapisu, f, indent=2, ensure_ascii=False)
            
            print(f'   ✅ Zachowano: {liczba_oczyszczonych} bezpiecznych wpisów')
            print(f'   🛡️  Wrażliwe dane TRWALE USUNIĘTE')
        else:
            print(f'   ⚠️  Brak bezpiecznych danych do zachowania')
            
    except Exception as e:
        print(f'   ❌ Błąd: {e}')

def usun_wrazliwe_dane(tekst):
    """TRWALE usuwa wrażliwe dane - bez zapisywania co usunięto"""
    if not isinstance(tekst, str):
        tekst = str(tekst)
    
    # TRWALE usuń emaile
    tekst = re.sub(r'\S+@\S+', '[EMAIL_USUNIĘTY]', tekst)
    
    # TRWALE usuń telefony
    tekst = re.sub(r'(\+?[\d\s\-\(\)]{9,})', '[TELEFON_USUNIĘTY]', tekst)
    
    # TRWALE usuń numery
    tekst = re.sub(r'(\d{4}[\s\-]?){3,}', '[NUMER_USUNIĘTY]', tekst)
    
    # TRWALE usuń wrażliwe słowa
    wrazliwe_slowa = ['hasło', 'password', 'login', 'email', 'telefon', 'numer', 
                     'pesel', 'dowód', 'karta', 'kredytowa', 'bank', 'pieniądze',
                     'adres', 'ulica', 'miasto', 'kod pocztowy']
    for slowo in wrazliwe_slowa:
        tekst = re.sub(re.escape(slowo), '[***]', tekst, flags=re.IGNORECASE)
    
    return tekst

def czy_wartosciowa_rozmowa(tekst):
    """Sprawdza czy rozmowa jest wartościowa do nauki"""
    if not isinstance(tekst, str):
        tekst = str(tekst)
    
    tekst = tekst.lower()
    
    # Odrzuć negatywne tematy
    niewlasciwe_tematy = ['przegrana', 'porażka', 'problem', 'kłopot', 'błąd', 
                         'niepowodzenie', 'nie udało', 'nie umiem', 'nie wiem']
    for temat in niewlasciwe_tematy:
        if temat in tekst:
            return False
    
    # Odrzuć za krótkie
    slowa = tekst.split()
    if len(slowa) < 3:
        return False
    
    return True

# PRZETWARZANIE
print('Rozpoczynam BEZPIECZNE oczyszczanie...')
print('🛡️  ŻADNE wrażliwe dane nie będą zapisane w raportach!')

for plik in os.listdir(czaty_path):
    if plik.endswith('.json'):
        sciezka = os.path.join(czaty_path, plik)
        bezpieczne_oczyszczanie(sciezka, plik)

print(f'\\n🎯 BEZPIECZNE OCZYSZCZANIE ZAKOŃCZONE!')
print(f'📁 Bezpieczne dane: {oczyszczone_path}')
print(f'🔥 Wrażliwe dane TRWALE USUNIĘTE - BRAK ŚLADÓW!')
print(f'🧠 Ollama nauczy się tylko CZYSTYCH, BEZPIECZNYCH rozmów!')
