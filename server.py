from flask import Flask, request, jsonify, redirect
import yt_dlp

app = Flask(__name__)

@app.route('/audio')
def get_audio():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'No video ID provided'}), 400
    url = f'https://www.youtube.com/watch?v={video_id}'
    ydl_opts = {'format': 'bestaudio[ext=m4a]/bestaudio/best', 'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return redirect(info['url'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ping')
def ping():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)