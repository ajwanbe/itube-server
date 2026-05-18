from flask import Flask, request, Response
import yt_dlp
import requests

app = Flask(__name__)

@app.route("/ping")
def ping():
    return "OK"

@app.route("/audio")
def audio():
    video_id = request.args.get("id")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/watch?v={video_id}",
            download=False
        )

    audio_url = info['url']

    r = requests.get(audio_url, stream=True)

    return Response(
        r.iter_content(chunk_size=1024),
        content_type=r.headers.get('Content-Type', 'audio/mpeg')
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
