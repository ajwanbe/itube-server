from flask import Flask, request
import yt_dlp

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
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )

        audio_url = info.get("url")

        if not audio_url:
            return "No audio url found", 500

        return audio_url

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
