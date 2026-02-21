from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Serwer ALFA działa lokalnie!"}

@app.post("/api/event")
async def handle_event(request: Request):
    data = await request.json()
    device_id = data.get("device_id", "unknown")
    event_type = data.get("event_type", "unknown")
    confidence = data.get("confidence", 0.0)

    print(f"[EVENT] {event_type.upper()} | confidence={confidence}")

    # Symulowana logika bezpieczeństwa
    risk = "HIGH" if confidence > 0.9 else "LOW"
    action = "ISOLATE_DEVICE" if risk == "HIGH" else "ALLOW"

    response = {
        "status": "ok",
        "device": device_id,
        "risk": risk,
        "action": action,
        "event_type": event_type
    }
    print("[CODEX]", json.dumps(response, indent=2))
    return response
