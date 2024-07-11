import os
from flask import Flask, request, jsonify, send_file
import yt_dlp
import io

app = Flask(__name__)

@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    data = request.get_json()
    video_url = data.get('url')
    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '-',  # Use `-` to indicate that the output is a stream
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            title = info_dict.get('title', 'audio')
            buffer = io.BytesIO()
            ydl.download([video_url])
            buffer.seek(0)

            # Save the file locally (optional)
            file_path = f"/tmp/{title}.mp3"  # Using /tmp directory
            with open(file_path, 'wb') as f:
                f.write(buffer.read())

            # Generate download URL
            download_url = request.url_root + 'download/' + title

            return jsonify({
                "title": title,
                "download_url": download_url
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<title>', methods=['GET'])
def download(title):
    file_path = f"/tmp/{title}.mp3"  # Using /tmp directory
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"{title}.mp3", mimetype='audio/mpeg')
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)