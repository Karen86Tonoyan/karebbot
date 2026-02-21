import queue, json, requests, sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3

# Ścieżka do modelu VOSK (upewnij się, że folder istnieje)
VOSK_PATH = "vosk-model-small-pl-0.22"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Inicjalizacja Vosk i kolejek audio
model = Model(VOSK_PATH)
rec = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

# Głos Aria (offline)
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.setProperty('volume', 0.9)
    voices = engine.getProperty('voices')
    for v in voices:
        if "female" in v.name.lower():
            engine.setProperty('voice', v.id)
            break
    engine.say(text)
    engine.runAndWait()

# Odpowiedź z Ollamy
def ask_ollama(prompt):
    try:
        payload = {"model": "mistral:7b", "prompt": prompt}
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        data = response.json()
        reply = data.get("response", "").strip()
        print(f"\n🤖 OLLAMA: {reply}")
        speak(reply)
    except Exception as e:
        print("⚠️ Błąd komunikacji z Ollamą:", e)

# Callback audio (zbiera dane z mikrofonu)
def callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

# Główna pętla nasłuchiwania
def listen():
    print("🎙️ Powiedz coś... (CTRL+C aby zakończyć)")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print(f"\n🗣️ Ty: {text}")
                    ask_ollama(text)

if __name__ == "__main__":
    try:
        speak("System ALFA Voice uruchomiony.")
        listen()
    except KeyboardInterrupt:
        print("\nZakończono nasłuchiwanie.")
        speak("Do zobaczenia.")
import queue, json, requests, sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3

# Ścieżka do modelu VOSK (upewnij się, że folder istnieje)
VOSK_PATH = "vosk-model-small-pl-0.22"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Inicjalizacja Vosk i kolejek audio
model = Model(VOSK_PATH)
rec = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

# Głos Aria (offline)
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.setProperty('volume', 0.9)
    voices = engine.getProperty('voices')
    for v in voices:
        if "female" in v.name.lower():
            engine.setProperty('voice', v.id)
            break
    engine.say(text)
    engine.runAndWait()

# Odpowiedź z Ollamy
def ask_ollama(prompt):
    try:
        payload = {"model": "mistral:7b", "prompt": prompt}
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        data = response.json()
        reply = data.get("response", "").strip()
        print(f"\n🤖 OLLAMA: {reply}")
        speak(reply)
    except Exception as e:
        print("⚠️ Błąd komunikacji z Ollamą:", e)

# Callback audio (zbiera dane z mikrofonu)
def callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

# Główna pętla nasłuchiwania
def listen():
    print("🎙️ Powiedz coś... (CTRL+C aby zakończyć)")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print(f"\n🗣️ Ty: {text}")
                    ask_ollama(text)

if __name__ == "__main__":
    try:
        speak("System ALFA Voice uruchomiony.")
        listen()
    except KeyboardInterrupt:
        print("\nZakończono nasłuchiwanie.")
        speak("Do zobaczenia.")
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
        audio = r.listen(source)
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
