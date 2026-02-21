"""
Detektor stanu emocjonalnego dla ALFA Bridge
Rozpoznaje panikę, lęk, chaos na podstawie tekstu
"""

import re


class EmotionDetector:
    """Wykrywa stan emocjonalny z tekstu"""
    
    PANIC_PATTERNS = [
        r"nie mog[ęę] oddycha[ćc]",
        r"serc[eo].*wal[ił]",
        r"umr[ęe]",
        r"co[śs] si[ęe] stan[ie]",
        r"zaraz si[ęe] zacznie",
        r"ALARM",
        r"panika",
        r"pomóc",
        r"ratunku"
    ]
    
    ANXIETY_PATTERNS = [
        r"co je[śs]li",
        r"boję się",
        r"l[ęe]k",
        r"strach",
        r"niepokój"
    ]
    
    CHAOS_INDICATORS = [
        lambda t: t.isupper(),  # CAPS LOCK
        lambda t: len(re.findall(r'\.\.\.', t)) > 2,  # wielokropki
        lambda t: len(t.split()) < 5 and '!' in t,  # krótkie + wykrzykniki
    ]
    
    @staticmethod
    def detect_state(text: str) -> dict:
        """
        Zwraca:
        {
            'level': 'PANIC' | 'PRE_PANIC' | 'ANXIETY' | 'STABLE',
            'intensity': 0-10,
            'indicators': [lista wykrytych sygnałów]
        }
        """
        text_lower = text.lower()
        indicators = []
        
        # Sprawdź kody bezpieczeństwa
        if "ALARM" in text or "alarm" in text:
            return {'level': 'PANIC', 'intensity': 10, 'indicators': ['CODE_ALARM']}
        
        if "KURA" in text or "kura" in text:
            return {'level': 'RESET', 'intensity': 0, 'indicators': ['CODE_KURA']}
        
        # Sprawdź panikę
        panic_score = 0
        for pattern in EmotionDetector.PANIC_PATTERNS:
            if re.search(pattern, text_lower):
                panic_score += 3
                indicators.append(pattern)
        
        # Sprawdź chaos w tekście
        chaos_score = sum(1 for check in EmotionDetector.CHAOS_INDICATORS if check(text))
        
        # Sprawdź lęk
        anxiety_score = 0
        for pattern in EmotionDetector.ANXIETY_PATTERNS:
            if re.search(pattern, text_lower):
                anxiety_score += 1
        
        total_score = panic_score + chaos_score + anxiety_score
        
        # Klasyfikacja
        if panic_score >= 3 or chaos_score >= 2:
            return {'level': 'PANIC', 'intensity': min(10, total_score), 'indicators': indicators}
        elif panic_score > 0 or "czuję że" in text_lower:
            return {'level': 'PRE_PANIC', 'intensity': min(7, total_score), 'indicators': indicators}
        elif anxiety_score > 0:
            return {'level': 'ANXIETY', 'intensity': min(5, anxiety_score), 'indicators': indicators}
        else:
            return {'level': 'STABLE', 'intensity': 0, 'indicators': []}
