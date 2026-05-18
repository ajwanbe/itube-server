from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "YOUR_JAMENDO_KEY"

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

@app.route("/audio")
def audio():
    track_id = request.args.get("id")

    url = f"https://api.jamendo.com/v3.0/tracks/?client_id={API_KEY}&format=json&id={track_id}"

    r = requests.get(url)
    data = r.json()

    if data["results"]:
        return data["results"][0]["audio"]

    return "not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
