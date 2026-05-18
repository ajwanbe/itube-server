from flask import Flask, request, Response, jsonify
import requests
 
app = Flask(__name__)
API_KEY = "d715b0eb"
 
@app.route("/ping")
def ping():
    return "OK"
 
@app.route("/search")
def search():
    q = request.args.get("q", "")
    url = f"https://api.jamendo.com/v3.0/tracks/?client_id={API_KEY}&format=json&limit=10&namesearch={q}"
    r = requests.get(url, timeout=10)
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
    # التطبيق يرسل ?id= (Jamendo track ID)
    track_id = request.args.get("id")
    
    # دعم القديم ?url= أيضاً
    audio_url = request.args.get("url")
 
    if not track_id and not audio_url:
        return "Missing id or url", 400
 
    # إذا عندنا track_id، نجيب رابط الصوت من Jamendo
    if track_id and not audio_url:
        jamendo_url = f"https://api.jamendo.com/v3.0/tracks/?client_id={API_KEY}&format=json&id={track_id}"
        try:
            resp = requests.get(jamendo_url, timeout=10)
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return "Track not found", 404
            audio_url = results[0]["audio"]
        except Exception as e:
            return f"Error fetching track: {e}", 500
 
    # Stream الصوت
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Range": request.headers.get("Range", "bytes=0-")
        }
        r = requests.get(audio_url, headers=headers, stream=True, timeout=15)
        
        response_headers = {
            "Content-Type": "audio/mpeg",
            "Accept-Ranges": "bytes",
        }
        if "Content-Length" in r.headers:
            response_headers["Content-Length"] = r.headers["Content-Length"]
        if "Content-Range" in r.headers:
            response_headers["Content-Range"] = r.headers["Content-Range"]
 
        return Response(
            r.iter_content(chunk_size=4096),
            status=r.status_code,
            headers=response_headers
        )
    except Exception as e:
        return f"Error streaming audio: {e}", 500
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
 














