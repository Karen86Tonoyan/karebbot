import os
import subprocess
import time

print("🚨 ALFA EMERGENCY SHUTDOWN")

# Lista procesów do zabicia
processes = ["ollama.exe", "python.exe", "node.exe", "esp32_monitor.exe"]

for proc in processes:
    try:
        result = subprocess.run(f"taskkill /F /IM {proc}", 
                              shell=True, 
                              capture_output=True)
        if result.returncode == 0:
            print(f"✅ Killed: {proc}")
        else:
            print(f"⚠️ Not running: {proc}")
    except Exception as e:
        print(f"❌ Error with {proc}: {e}")

# Log krytycznego zdarzenia
with open("critical_event.log", "a") as f:
    f.write(f"EMERGENCY SHUTDOWN at {time.ctime()}\n")

print("✅ ALFA EMERGENCY SHUTDOWN COMPLETE")