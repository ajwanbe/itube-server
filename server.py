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
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )

        # أهم نقطة: اختيار أول audio مناسب
        audio_url = None

        if "formats" in info:
            for f in info["formats"]:
                if f.get("acodec") != "none" and f.get("url"):
                    audio_url = f["url"]
                    break

        if not audio_url:
            audio_url = info.get("url")

        if not audio_url:
            return "No audio found", 500

        return audio_url

    except Exception as e:
        return f"ERROR: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
