import json
import os

print('=== PODGLĄD RAPORTU USUNIĘTYCH DANYCH ===')

raport_path = r'D:\kurlewski skarbiec\Analiza_Usuniętych\raport_usunietych_danych.json'

if not os.path.exists(raport_path):
    print('❌ Nie znaleziono raportu')
    exit()

with open(raport_path, 'r', encoding='utf-8') as f:
    raport = json.load(f)

print(f'📅 Data analizy: {raport["data_analizy"]}')
print(f'\\n📊 STATYSTYKI:')
for stat, wartosc in raport['statystyki'].items():
    print(f'   {stat}: {wartosc}')

print(f'\\n🔍 PRZYKŁADY USUNIĘTYCH DANYCH:')

if raport['znalezione_emaile']:
    print(f'\\n📧 USUNIĘTE EMAILE:')
    for email in raport['znalezione_emaile'][:3]:
        print(f'   - {email["email"]} (z: {email["zrodlo"]})')

if raport['znalezione_telefony']:
    print(f'\\n📞 USUNIĘTE TELEFONY:')
    for tel in raport['znalezione_telefony'][:3]:
        print(f'   - {tel["telefon"]} (z: {tel["zrodlo"]})')

if raport['usuniete_rozmowy']:
    print(f'\\n🗑️  USUNIĘTE ROZMOWY:')
    for rozmowa in raport['usuniete_rozmowy'][:5]:
        print(f'   - Powód: {rozmowa["powod"]}')
        print(f'     Tekst: {rozmowa["tekst"]}')
        print()

print(f'\\n🛡️  WSZYSTKIE TE DANE ZOSTAŁY USUNIĘTE DLA BEZPIECZEŃSTWA!')
