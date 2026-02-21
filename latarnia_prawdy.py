class LatarniaPrawdy:
    def __init__(self):
        self.wzorce_zdrady = [
            "nagła zmiana zachowania",
            "tajemnicze spotkania", 
            "ukrywanie informacji",
            "podwójna komunikacja",
            "izolowanie od zasobów",
            "unikanie kontaktu",
            "sprzeczne informacje",
            "nadmierna defensywność"
        ]
        self.dane_zdarzen = []
        
    def dodaj_zdarzenie(self, opis, osoba, data, rodzaj_zdarzenia):
        self.dane_zdarzen.append({
            'opis': opis,
            'osoba': osoba,
            'data': data,
            'rodzaj': rodzaj_zdarzenia
        })
        return f"✅ Zdarzenie dodane: {opis}"
    
    def skanuj_otoczenie(self):
        wykryte_anomalie = []
        for zdarzenie in self.dane_zdarzen:
            for wzorzec in self.wzorce_zdrady:
                if wzorzec in zdarzenie['opis'].lower():
                    wykryte_anomalie.append({
                        'wzorzec': wzorzec,
                        'zdarzenie': zdarzenie['opis'],
                        'osoba': zdarzenie['osoba']
                    })
        return wykryte_anomalie
    
    def generuj_raport(self):
        anomalie = self.skanuj_otoczenie()
        raport = "📊 RAPORT SYSTEMU LATARNIA PRAWDY\n"
        raport += "=" * 50 + "\n"
        
        if not anomalie:
            raport += "✅ BRAK WYKRYTYCH ANOMALII\n"
        else:
            raport += f"🚨 WYKRYTO {len(anomalie)} ANOMALII:\n\n"
            for i, anomalia in enumerate(anomalie, 1):
                raport += f"{i}. WZORZEC: {anomalia['wzorzec']}\n"
                raport += f"   OSOBA: {anomalia['osoba']}\n"
                raport += f"   ZDARZENIE: {anomalia['zdarzenie']}\n"
                raport += "   " + "-"*40 + "\n"
        
        return raport

# 🎯 TWORZENIE INSTANCJI SYSTEMU
system = LatarniaPrawdy()

# 📝 DODAWANIE PRZYKŁADOWYCH ZDARZEŃ
system.dodaj_zdarzenie(
    "Nagła zmiana zachowania - unika spotkań", 
    "Jan Kowalski", 
    "2024-01-15", 
    "zmiana_zachowania"
)

system.dodaj_zdarzenie(
    "Tajemnicze spotkania w godzinach pracy",
    "Anna Nowak", 
    "2024-01-16", 
    "tajne_spotkania"
)

# 🚨 GENEROWANIE RAPORTU
print(system.generuj_raport())
