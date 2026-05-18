from flask import Flask, request, redirect
import requests

app = Flask(__name__)

@app.route("/ping")
def ping():
    return "OK"

@app.route("/audio")
def audio():
    video_id = request.args.get("id")

    if not video_id:
        return "Missing video id", 400

    try:
        api_url = f"https://invidious.fdn.fr/api/v1/videos/{video_id}"

        r = requests.get(api_url, timeout=10)

        if r.status_code != 200:
            return "Failed to fetch video info", 500

        data = r.json()

        audio_formats = []

        for f in data.get("adaptiveFormats", []):
            if "audio" in f.get("type", ""):
                audio_formats.append(f)

        if not audio_formats:
            return "No audio streams found", 500

        audio_url = audio_formats[0]["url"]

        return redirect(audio_url)

    except Exception as e:
        return f"ERROR: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
