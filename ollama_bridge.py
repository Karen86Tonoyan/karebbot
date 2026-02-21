from flask import Flask, request, Response
import requests, os

app = Flask(__name__)

# 🧠 IP Predatora – wpisz tutaj adres drugiego komputera
TARGET = os.environ.get("PREDATOR_OLLAMA", "http://192.168.1.200:11434")
BRIDGE_TOKEN = os.environ.get("BRIDGE_TOKEN", "sekret")

def forward(path):
    url = f"{TARGET}{path}"
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    headers['X-Bridge-Token'] = BRIDGE_TOKEN
    r = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        params=request.args,
        data=request.get_data(),
        stream=True,
        timeout=60
    )
    return Response(r.iter_content(chunk_size=4096),
                    status=r.status_code,
                    headers=dict(r.headers))

@app.route('/api/<path:subpath>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def api_proxy(subpath):
    return forward(f"/api/{subpath}")

@app.route('/', defaults={'u': ''})
@app.route('/<path:u>')
def catch_all(u):
    return forward(f"/{u}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=11434)
