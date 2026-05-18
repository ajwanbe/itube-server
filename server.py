from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)
API_KEY = "d715b0eb"

@app.route("/ping")
def ping():
    return "OK"

# Search endpoint - returns YouTube-compatible format
# App calls: /search?q=QUERY&a=111...
@app.route("/search")
def search():
    q = request.args.get("q", "")
    url = f"https://api.jamendo.com/v3.0/tracks/?client_id={API_KEY}&format=json&limit=25&namesearch={q}&include=musicinfo"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except Exception as e:
        return jsonify({"nextPageToken": "", "items": []}), 200

    items = []
    for t in data.get("results", []):
        items.append({
            "id": {
                "videoId": str(t["id"])
            }
        })

    return jsonify({
        "nextPageToken": "",
        "items": items
    })

# Videos details endpoint - returns YouTube-compatible format
# App calls: /videos?id=JAMENDO_ID&t=...&f=...
# or:        /videos?id=JAMENDO_ID&k=...&f=...
@app.route("/videos")
def videos():
    track_id = request.args.get("id", "")
    # Handle comma-separated IDs
    ids = [i.strip() for i in track_id.split(",") if i.strip()]

    results = []
    for tid in ids:
        url = f"https://api.jamendo.com/v3.0/tracks/?client_id={API_KEY}&format=json&id={tid}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            tracks = data.get("results", [])
            if tracks:
                t = tracks[0]
                # Duration: Jamendo gives seconds, YouTube gives PT#M#S
                duration_sec = t.get("duration", 0)
                mins = duration_sec // 60
                secs = duration_sec % 60
                duration_str = f"PT{mins}M{secs}S"

                results.append({
                    "id": str(t["id"]),
                    "snippet": {
                        "title": t["name"],
                        "channelTitle": t["artist_name"],
                        "thumbnails": {
                            "default": {"url": t.get("album_image", "")},
                            "medium":  {"url": t.get("album_image", "")},
                            "high":    {"url": t.get("album_image", "")}
                        }
                    },
                    "contentDetails": {
                        "duration": duration_str
                    },
                    "statistics": {
                        "viewCount": "0",
                        "likeCount": "0"
                    }
                })
        except Exception as e:
            pass

    return jsonify({"items": results})

# Audio streaming endpoint
# App calls: /audio?id=JAMENDO_TRACK_ID
@app.route("/audio")
def audio():
    track_id = request.args.get("id")
    audio_url = request.args.get("url")

    if track_id and not audio_url:
        # Get audio URL from Jamendo
        url = f"https://api.jamendo.com/v3.0/tracks/?client_id={API_KEY}&format=json&id={track_id}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            tracks = data.get("results", [])
            if tracks:
                audio_url = tracks[0].get("audio")
        except Exception as e:
            return f"Error fetching track: {e}", 500

    if not audio_url:
        return "Track not found", 404

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36",
            "Range": request.headers.get("Range", "bytes=0-")
        }
        r = requests.get(audio_url, headers=headers, stream=True, timeout=30)
        
        response_headers = {
            "Content-Type": "audio/mpeg",
            "Accept-Ranges": "bytes",
        }
        if "Content-Length" in r.headers:
            response_headers["Content-Length"] = r.headers["Content-Length"]
        if "Content-Range" in r.headers:
            response_headers["Content-Range"] = r.headers["Content-Range"]

        return Response(
            r.iter_content(chunk_size=8192),
            status=r.status_code,
            headers=response_headers
        )
    except Exception as e:
        return f"Error streaming audio: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
