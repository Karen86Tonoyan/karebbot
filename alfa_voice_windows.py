import speech_recognition as sr
import requests
import pyttsx3

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

r = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 0.9)

print("🎙️ ALFA Voice (Windows) aktywny – mów po polsku.")

while True:
    with sr.Microphone() as source:
        print("\nSłucham...")
        # Parametry cierpliwości i długości wypowiedzi
        r.pause_threshold = 1.2        # ile sekund ciszy uznaje za koniec wypowiedzi
        r.non_speaking_duration = 0.5  # ignoruj krótkie oddechy
        audio = r.listen(source, phrase_time_limit=5)  # maks. 5 sekund na wypowiedź

    try:
        text = r.recognize_google(audio, language="pl-PL")
        print("🗣️ Ty:", text)

        data = {"model": "mistral:7b", "prompt": text}
        reply = requests.post(OLLAMA_URL, json=data, timeout=120).json()["response"]
        print("🤖 ALFA:", reply)

        engine.say(reply)
        engine.runAndWait()

    except sr.UnknownValueError:
        print("❓ Nie zrozumiałem – powtórz.")
    except Exception as e:
        print("⚠️ Błąd:", e)
