from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Flask działa! 🔥</h1>"

if __name__ == "__main__":
    print("✅ Serwer Flask wystartował na porcie 5050 - from flask import Flask.py:10")
    app.run(debug=True, port=5050, host="0.0.0.0")
