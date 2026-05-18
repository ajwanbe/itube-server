from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "d715b0eb"

@app.route("/ping")
def ping():
    return "OK"

@app.route("/search")
def search():
    q = request.args.get("q")

    url = f"https://api.jamendo.com/v3.0/tracks/?client_id={API_KEY}&format=json&limit=10&namesearch={q}"

    r = requests.get(url)
    data = r.json()

    results = []

    for t in data.get("results", []):
        results.append({
            "id": t["id"],
            "title": t["name"],
            "artist": t["artist_name"],
            "audio": t["audio"],
            "image": t["album_image"]
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
