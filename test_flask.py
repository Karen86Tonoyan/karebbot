from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Flask działa poprawnie 🐍</h1>"

if __name__ == "__main__":
    print("✅ Uruchamiam Flask na porcie 5050...")
    app.run(debug=True, port=5050, host="0.0.0.0")
